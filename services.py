"""
Carbon footprint computation services using efficient SQLAlchemy queries.
"""
from collections import defaultdict

from sqlalchemy import func
from sqlalchemy.orm import aliased

from zou.app import db
from zou.app.models.time_spent import TimeSpent
from zou.app.models.task import Task
from zou.app.models.task_type import TaskType
from zou.app.models.entity import Entity
from zou.app.models.entity_type import EntityType
from zou.app.models.person import Person

from .models import CarbonFactor


DEFAULT_COUNTRY = "FR"


def _get_person_country(person):
    """
    Get country code from a person.
    Checks for country column first, then falls back to data JSONB field.
    Defaults to France if no location is found.
    """
    if hasattr(person, "country") and person.country:
        return person.country
    if person.data and isinstance(person.data, dict):
        return person.data.get("country", DEFAULT_COUNTRY)
    return DEFAULT_COUNTRY


def get_sequence_footprint_data(project_id):
    """
    Get CO2 footprint data grouped by sequence and task type.
    Returns raw data for the resource to format.

    Uses a single query with JOINs instead of N+1 queries.
    """
    Sequence = aliased(Entity)

    query = (
        db.session.query(
            TimeSpent.duration,
            Task.id.label("task_id"),
            TaskType.id.label("task_type_id"),
            TaskType.name.label("task_type_name"),
            Sequence.id.label("sequence_id"),
            Sequence.name.label("sequence_name"),
            Person.id.label("person_id"),
            Person.data.label("person_data"),
        )
        .join(Task, TimeSpent.task_id == Task.id)
        .join(TaskType, Task.task_type_id == TaskType.id)
        .join(Entity, Task.entity_id == Entity.id)
        .join(Sequence, Entity.parent_id == Sequence.id)
        .join(Person, TimeSpent.person_id == Person.id)
        .filter(Task.project_id == project_id)
        .filter(Sequence.id.isnot(None))
    )

    if hasattr(Person, "country"):
        query = query.add_columns(Person.country.label("person_country"))

    return _process_footprint_query(
        query.all(),
        group_key="sequence",
        has_country_column=hasattr(Person, "country"),
    )


def get_episode_footprint_data(project_id):
    """
    Get CO2 footprint data grouped by episode and task type.
    For TV series, episodes are the parent of sequences.

    Uses a single query with JOINs.
    """
    Sequence = aliased(Entity)
    Episode = aliased(Entity)

    query = (
        db.session.query(
            TimeSpent.duration,
            Task.id.label("task_id"),
            TaskType.id.label("task_type_id"),
            TaskType.name.label("task_type_name"),
            Episode.id.label("episode_id"),
            Episode.name.label("episode_name"),
            Person.id.label("person_id"),
            Person.data.label("person_data"),
        )
        .join(Task, TimeSpent.task_id == Task.id)
        .join(TaskType, Task.task_type_id == TaskType.id)
        .join(Entity, Task.entity_id == Entity.id)
        .join(Sequence, Entity.parent_id == Sequence.id)
        .join(Episode, Sequence.parent_id == Episode.id)
        .join(Person, TimeSpent.person_id == Person.id)
        .filter(Task.project_id == project_id)
        .filter(Episode.id.isnot(None))
    )

    if hasattr(Person, "country"):
        query = query.add_columns(Person.country.label("person_country"))

    return _process_footprint_query(
        query.all(),
        group_key="episode",
        has_country_column=hasattr(Person, "country"),
    )


def get_asset_footprint_data(project_id):
    """
    Get CO2 footprint data grouped by asset type and task type.

    Uses a single query with JOINs.
    """
    query = (
        db.session.query(
            TimeSpent.duration,
            Task.id.label("task_id"),
            TaskType.id.label("task_type_id"),
            TaskType.name.label("task_type_name"),
            EntityType.id.label("asset_type_id"),
            EntityType.name.label("asset_type_name"),
            Person.id.label("person_id"),
            Person.data.label("person_data"),
        )
        .join(Task, TimeSpent.task_id == Task.id)
        .join(TaskType, Task.task_type_id == TaskType.id)
        .join(Entity, Task.entity_id == Entity.id)
        .join(EntityType, Entity.entity_type_id == EntityType.id)
        .join(Person, TimeSpent.person_id == Person.id)
        .filter(Task.project_id == project_id)
        .filter(EntityType.name != "Shot")
        .filter(EntityType.name != "Sequence")
        .filter(EntityType.name != "Episode")
    )

    if hasattr(Person, "country"):
        query = query.add_columns(Person.country.label("person_country"))

    return _process_footprint_query(
        query.all(),
        group_key="asset_type",
        has_country_column=hasattr(Person, "country"),
    )


def get_task_type_footprint_data(project_id):
    """
    Get CO2 footprint data grouped by task type only.
    Simple view for production-level breakdown.
    """
    query = (
        db.session.query(
            TimeSpent.duration,
            TaskType.id.label("task_type_id"),
            TaskType.name.label("task_type_name"),
            Person.id.label("person_id"),
            Person.data.label("person_data"),
        )
        .join(Task, TimeSpent.task_id == Task.id)
        .join(TaskType, Task.task_type_id == TaskType.id)
        .join(Person, TimeSpent.person_id == Person.id)
        .filter(Task.project_id == project_id)
    )

    if hasattr(Person, "country"):
        query = query.add_columns(Person.country.label("person_country"))

    rows = query.all()
    has_country_column = hasattr(Person, "country")

    carbon_factors = {f.country_code: f.workbench_co2e for f in
                      CarbonFactor.query.all()}

    breakdown = defaultdict(lambda: {
        "co2_grams": 0.0,
        "duration_minutes": 0,
    })
    total_co2 = 0.0
    total_duration = 0

    for row in rows:
        duration_minutes = row.duration or 0
        task_type_id = row.task_type_id
        task_type_name = row.task_type_name or "Unknown"

        if has_country_column:
            country = row.person_country
        else:
            country = None
            if row.person_data and isinstance(row.person_data, dict):
                country = row.person_data.get("country")

        co2 = 0.0
        if country and country in carbon_factors:
            hours = duration_minutes / 60.0
            co2 = hours * carbon_factors[country]

        breakdown[task_type_id]["co2_grams"] += co2
        breakdown[task_type_id]["duration_minutes"] += duration_minutes
        breakdown[task_type_id]["task_type_name"] = task_type_name

        total_co2 += co2
        total_duration += duration_minutes

    details = []
    for tt_id, data in breakdown.items():
        details.append({
            "task_type_id": tt_id,
            "task_type_name": data.get("task_type_name", "Unknown"),
            "co2_grams": round(data["co2_grams"], 2),
            "co2_kg": round(data["co2_grams"] / 1000, 4),
            "duration_minutes": data["duration_minutes"],
        })

    return {
        "details": details,
        "total_co2_grams": total_co2,
        "total_duration_minutes": total_duration,
    }


def get_studio_footprint_data():
    """
    Get CO2 footprint data for all productions, grouped by production and
    task type. Studio-level view across all projects.
    """
    from zou.app.models.project import Project

    query = (
        db.session.query(
            TimeSpent.duration,
            Task.project_id.label("project_id"),
            Project.name.label("project_name"),
            TaskType.id.label("task_type_id"),
            TaskType.name.label("task_type_name"),
            Person.id.label("person_id"),
            Person.data.label("person_data"),
        )
        .join(Task, TimeSpent.task_id == Task.id)
        .join(Project, Task.project_id == Project.id)
        .join(TaskType, Task.task_type_id == TaskType.id)
        .join(Person, TimeSpent.person_id == Person.id)
    )

    if hasattr(Person, "country"):
        query = query.add_columns(Person.country.label("person_country"))

    return _process_footprint_query(
        query.all(),
        group_key="project",
        has_country_column=hasattr(Person, "country"),
    )


def get_summary_footprint_data(project_id):
    """
    Get overall CO2 footprint summary for a project.

    Uses a single query with JOINs.
    """
    query = (
        db.session.query(
            TimeSpent.duration,
            TimeSpent.date,
            Person.id.label("person_id"),
            Person.data.label("person_data"),
        )
        .join(Task, TimeSpent.task_id == Task.id)
        .join(Person, TimeSpent.person_id == Person.id)
        .filter(Task.project_id == project_id)
    )

    if hasattr(Person, "country"):
        query = query.add_columns(Person.country.label("person_country"))

    rows = query.all()
    has_country_column = hasattr(Person, "country")

    carbon_factors = {f.country_code: f.workbench_co2e for f in
                      CarbonFactor.query.all()}

    total_co2 = 0.0
    total_duration = 0
    weekly_data = defaultdict(lambda: {"co2_grams": 0.0, "minutes": 0})

    for row in rows:
        duration_minutes = row.duration or 0

        if has_country_column:
            country = row.person_country
        else:
            country = None
            if row.person_data and isinstance(row.person_data, dict):
                country = row.person_data.get("country")

        co2 = 0.0
        if country and country in carbon_factors:
            hours = duration_minutes / 60.0
            co2 = hours * carbon_factors[country]

        total_co2 += co2
        total_duration += duration_minutes

        if row.date:
            week_key = row.date.strftime("%Y-%m")
            weekly_data[week_key]["co2_grams"] += co2
            weekly_data[week_key]["minutes"] += duration_minutes

    num_weeks = max(len(weekly_data), 1)
    weekly_avg_co2 = total_co2 / num_weeks

    return {
        "total_co2_grams": total_co2,
        "total_duration_minutes": total_duration,
        "weekly_average_co2_grams": weekly_avg_co2,
        "num_weeks_with_data": num_weeks,
    }


def _process_footprint_query(rows, group_key, has_country_column):
    """
    Process query results and compute CO2 footprint.

    Args:
        rows: Query result rows
        group_key: Key for grouping ("sequence", "episode", or "asset_type")
        has_country_column: Whether Person has a country column

    Returns:
        Dict with details, aggregates, and totals
    """
    carbon_factors = {f.country_code: f.workbench_co2e for f in
                      CarbonFactor.query.all()}

    breakdown = defaultdict(lambda: defaultdict(lambda: {
        "co2_grams": 0.0,
        "duration_minutes": 0,
    }))
    by_task_type = defaultdict(lambda: {"co2_grams": 0.0})
    by_group = defaultdict(lambda: {"co2_grams": 0.0})
    total_co2 = 0.0
    total_duration = 0

    group_id_field = f"{group_key}_id"
    group_name_field = f"{group_key}_name"

    for row in rows:
        duration_minutes = row.duration or 0
        group_id = getattr(row, group_id_field)
        group_name = getattr(row, group_name_field, "Unknown")
        task_type_id = row.task_type_id
        task_type_name = row.task_type_name or "Unknown"

        if has_country_column:
            country = getattr(row, "person_country", None)
        else:
            country = None
            if row.person_data and isinstance(row.person_data, dict):
                country = row.person_data.get("country")

        co2 = 0.0
        if country and country in carbon_factors:
            hours = duration_minutes / 60.0
            co2 = hours * carbon_factors[country]

        breakdown[group_id][task_type_id]["co2_grams"] += co2
        breakdown[group_id][task_type_id]["duration_minutes"] += (
            duration_minutes
        )
        breakdown[group_id][task_type_id]["group_name"] = group_name
        breakdown[group_id][task_type_id]["task_type_name"] = task_type_name

        by_task_type[task_type_name]["co2_grams"] += co2
        by_group[group_name]["co2_grams"] += co2
        total_co2 += co2
        total_duration += duration_minutes

    details = []
    for grp_id, task_types in breakdown.items():
        for tt_id, data in task_types.items():
            detail = {
                f"{group_key}_id": grp_id,
                f"{group_key}_name": data.get("group_name", "Unknown"),
                "task_type_id": tt_id,
                "task_type_name": data.get("task_type_name", "Unknown"),
                "co2_grams": round(data["co2_grams"], 2),
                "co2_kg": round(data["co2_grams"] / 1000, 4),
                "duration_minutes": data["duration_minutes"],
            }
            details.append(detail)

    return {
        "details": details,
        "by_task_type": {
            k: {"co2_kg": round(v["co2_grams"] / 1000, 4)}
            for k, v in by_task_type.items()
        },
        f"by_{group_key}": {
            k: {"co2_kg": round(v["co2_grams"] / 1000, 4)}
            for k, v in by_group.items()
        },
        "total_co2_grams": total_co2,
        "total_duration_minutes": total_duration,
    }
