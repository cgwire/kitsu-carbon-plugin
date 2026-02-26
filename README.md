# Kitsu Carbon Tracking Plugin

Track the carbon footprint of your productions based on artist work time and country-specific emission factors.

## Features

- CO2 emissions computed from time spents and per-country carbon factors
- Studio-wide and per-production dashboards
- Matrix view (productions/sequences x task types) with color-coded impact
- Breakdown view with horizontal bar charts
- Weekly change tracking
- Unit toggle (kgCO2e / tCO2e)
- Pre-seeded emission factors for 23 countries

## Setup

### Requirements

- [Zou](https://github.com/cgwire/zou) (latest)
- Node.js 22+ (for frontend build)

### Install

```bash
# Install the plugin
zou install-plugin https://github.com/frankrousseau/kitsu-carbon-plugin
```

### Uninstall

```bash
zou uninstall-plugin carbon
```

## Development

### Backend

```bash
# Format code
black --line-length 80 *.py

# Run tests
pip install -e .
pytest tests/ -v
```

### Frontend

```bash
cd frontend

# Start dev server (proxies /api to Zou on port 5000)
npm run dev

# Lint & format
npm run lint

# Production build
npm run build
```

## Documentation

- [SPECS.md](./SPECS.md) — API endpoints, data model, computation logic
- [FRONTEND_SPECS.md](./FRONTEND_SPECS.md) — UI components, color palette, store
- [KITSU_PLUGIN_GUIDE.md](./KITSU_PLUGIN_GUIDE.md) — Generic Kitsu plugin conventions
