"""
Pytest configuration and fixtures for carbon plugin tests.

Requirements:
    - zou must be installed with test dependencies: pip install zou[test]
    - Plugin must be installed: pip install -e .
"""
import pytest

from zou.app import db
from zou.app.models.person import Person

from carbon.models import CarbonFactor


@pytest.fixture
def carbon_factors():
    """
    Create carbon factors for testing.
    """
    factors = [
        CarbonFactor(
            country_code="FR",
            country_name="France",
            rendering_co2e=12.0,
            workbench_co2e=10.0,
        ),
        CarbonFactor(
            country_code="US",
            country_name="United States",
            rendering_co2e=95.0,
            workbench_co2e=58.0,
        ),
        CarbonFactor(
            country_code="DE",
            country_name="Germany",
            rendering_co2e=80.0,
            workbench_co2e=50.0,
        ),
    ]
    for factor in factors:
        db.session.add(factor)
    db.session.commit()
    return factors


def set_person_country(person_id, country_code):
    """
    Set country for a person (via data JSONB field since country column
    may not exist yet).
    """
    person = Person.query.get(person_id)
    if person:
        if person.data is None:
            person.data = {}
        person.data["country"] = country_code
        db.session.commit()
    return person
