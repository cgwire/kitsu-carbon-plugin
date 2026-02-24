# Carbon Tracking Plugin - Specifications

## Overview

A Kitsu plugin to track carbon consumption of productions based on artist work time and location-based emission factors.

## Data Model

### CarbonFactor Table

| Column | Type | Description |
|--------|------|-------------|
| `country_code` | String(2), PK | ISO 3166-1 alpha-2 code |
| `country_name` | String(80) | Country name |
| `rendering_co2e` | Float | g CO2e per hour for rendering |
| `workbench_co2e` | Float | g CO2e per hour for workbench |

Pre-populated with 23 countries on install.

## API Endpoints

All routes prefixed with `/api/plugins/carbon/`

### Carbon Factors

#### GET /factors
List all carbon emission factors.

**Response:**
```json
[
  {
    "country_code": "FR",
    "country_name": "France",
    "rendering_co2e": 12.0,
    "workbench_co2e": 10.0
  }
]
```

#### GET /factors/<country_code>
Get emission factor for a specific country.

**Response:**
```json
{
  "country_code": "FR",
  "country_name": "France",
  "rendering_co2e": 12.0,
  "workbench_co2e": 10.0
}
```

#### POST /factors
Create or update a carbon factor (admin only).

**Request:**
```json
{
  "country_code": "FR",
  "country_name": "France",
  "rendering_co2e": 12.0,
  "workbench_co2e": 10.0
}
```

### Production Footprint

#### GET /productions/<project_id>/footprint/sequences
CO2 footprint breakdown by sequence and task type (for features/shorts).

**Response:**
```json
{
  "project_id": "uuid",
  "project_name": "My Project",
  "details": [
    {
      "sequence_id": "uuid",
      "sequence_name": "SEQ01",
      "task_type_id": "uuid",
      "task_type_name": "Animation",
      "co2_grams": 120.5,
      "co2_kg": 0.1205,
      "duration_minutes": 480
    }
  ],
  "by_task_type": {
    "Animation": {"co2_kg": 0.1205},
    "Lighting": {"co2_kg": 0.0852}
  },
  "by_sequence": {
    "SEQ01": {"co2_kg": 0.2057}
  },
  "total_co2_kg": 0.2057,
  "total_duration_minutes": 800,
  "total_man_days": 1.67
}
```

#### GET /productions/<project_id>/footprint/episodes
CO2 footprint breakdown by episode and task type (for TV series).

**Response:** Same structure as sequences, with `episode_id`, `episode_name`, `by_episode`.

#### GET /productions/<project_id>/footprint/assets
CO2 footprint breakdown by asset type and task type.

**Response:** Same structure, with `asset_type_id`, `asset_type_name`, `by_asset_type`.

#### GET /productions/<project_id>/footprint/summary
Overall CO2 footprint summary.

**Response:**
```json
{
  "project_id": "uuid",
  "project_name": "My Project",
  "total_co2_kg": 15.234,
  "total_duration_minutes": 48000,
  "total_man_days": 100.0,
  "weekly_average_co2_kg": 1.523,
  "num_weeks_with_data": 10
}
```

## Computation Logic

```
CO2 = SUM(time_spent.duration * carbon_factor.workbench_co2e)
      for each person's time spent, using their country's factor
```

- Duration is in minutes, converted to hours for calculation
- CO2 factors are in grams per hour
- Results displayed in both grams and kilograms
- Man days calculated as: `duration_minutes / 60 / 8`

## Architecture

### Files

| File | Purpose |
|------|---------|
| `manifest.toml` | Plugin metadata |
| `models.py` | CarbonFactor SQLAlchemy model |
| `services.py` | Efficient SQLAlchemy queries |
| `resources.py` | Flask-RESTful API endpoints |
| `__init__.py` | Routes and lifecycle hooks |
| `migrations/` | Alembic database migrations |

### Query Strategy

Uses efficient SQLAlchemy JOINs instead of N+1 queries:

```
TimeSpent → Task → TaskType → Entity → Sequence/Episode → Person → CarbonFactor
```

Single query per endpoint, aggregation done in Python.

## Dependencies

Relies on Zou models:
- `TimeSpent` - work time entries
- `Task` - tasks with entity and task_type references
- `Entity` - shots, sequences, episodes, assets
- `EntityType` - asset types
- `TaskType` - task type definitions
- `Person` - artist info (requires `country` field or `data.country`)

## Installation

```bash
zou install-plugin /path/to/carbon
```

This will:
1. Run the Alembic migration to create `plugin_carbon_factors` table
2. Seed initial carbon factor data for 23 countries via `post_install` hook

## Pre-seeded Countries

AU, BE, BR, CA, CN, DE, DK, ES, FI, FR, GB, IN, IT, JP, KR, MX, NL, NO, NZ, PL, SE, US, ZA

## Testing

### Running Tests

**Requirements:**
- `zou` must be installed with test utilities exposed (`zou.tests.base`)
- Plugin must be installed: `pip install -e .`

```bash
cd /path/to/plugins/carbon

# Run all tests
pytest tests/ -v

# Run only service tests
pytest tests/test_services.py -v

# Run only resource/API tests
pytest tests/test_resources.py -v

# Run a specific test class
pytest tests/test_services.py::SequenceFootprintTestCase -v
```

**Note:** Tests depend on `zou.tests.base.ApiDBTestCase`. If zou doesn't package its test utilities, zou may need to expose them via:
- Adding `tests` to `packages` in `setup.py`
- Or creating a separate `zou-test-utils` package

### Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Fixtures and helpers
├── test_services.py     # Service layer tests
└── test_resources.py    # API endpoint tests
```

### Test Cases

**Service Tests (`test_services.py`):**
- `SequenceFootprintTestCase` - Tests for sequence footprint computation
- `AssetFootprintTestCase` - Tests for asset footprint computation
- `EpisodeFootprintTestCase` - Tests for episode footprint (TV series)
- `SummaryFootprintTestCase` - Tests for overall summary
- `CarbonFactorModelTestCase` - Tests for the CarbonFactor model

**Resource Tests (`test_resources.py`):**
- `CarbonFactorsResourceTestCase` - Tests for `/factors` endpoints
- `SequenceFootprintResourceTestCase` - Tests for sequence footprint API
- `AssetFootprintResourceTestCase` - Tests for asset footprint API
- `EpisodeFootprintResourceTestCase` - Tests for episode footprint API
- `SummaryFootprintResourceTestCase` - Tests for summary API
- `AccessControlTestCase` - Tests for authentication/authorization

### Test Data Setup

Tests use Zou's `ApiDBTestCase` base class which provides:
- Automatic database setup/teardown with transactions
- Fixture generators (`generate_fixture_project()`, `generate_fixture_task()`, etc.)
- Authentication helpers (`log_in_admin()`, `log_in_cg_artist()`)
- HTTP method helpers (`get()`, `post()`, `put()`, `delete()`)
