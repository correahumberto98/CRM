"""The configured contact form contract, including legacy data preservation."""

import pytest

from contacts.models import Contact


@pytest.mark.django_db
def test_full_name_and_optional_fields_round_trip(admin_client):
    payload = {
        "name": "María del Carmen",
        "phone": "+1 305 555 0199",
        "source": "META",
        "stage": "LEAD",
        "address_line": "123 Demo St",
        "city": "Miami",
        "postcode": "00123",
        "state": "Florida",
        "preferred_communication_channel": "SMS",
        "description": "Prefers afternoon calls",
    }
    response = admin_client.post("/api/contacts/", payload, format="json")
    assert response.status_code == 200, response.data
    contact = Contact.objects.get(first_name=payload["name"])
    data = admin_client.get(f"/api/contacts/{contact.id}/").data["contact_obj"]
    for key, value in payload.items():
        assert data[key] == value
    assert data["last_name"] == ""
    assert data["email"] is None


@pytest.mark.django_db
@pytest.mark.parametrize("missing", ["name", "phone", "source", "stage"])
def test_required_fields_enforced_by_api(admin_client, missing):
    payload = {
        "name": "Demo",
        "phone": "3055550199",
        "source": "ORGANIC",
        "stage": "LEAD",
    }
    del payload[missing]
    response = admin_client.post("/api/contacts/", payload, format="json")
    assert response.status_code == 400
    assert missing in response.data["errors"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "field,value",
    [
        ("name", " "),
        ("phone", ""),
        ("phone", "abc"),
        ("source", "INVALID"),
        ("stage", "CLOSED_WON"),
        ("preferred_communication_channel", "FAX"),
    ],
)
def test_invalid_contact_values_rejected(admin_client, field, value):
    payload = {
        "name": "Demo",
        "phone": "3055550199",
        "source": "ORGANIC",
        "stage": "LEAD",
        field: value,
    }
    response = admin_client.post("/api/contacts/", payload, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_legacy_name_and_unknown_fields_preserved(admin_client, org_a, admin_user):
    c = Contact.objects.create(
        first_name="María", last_name="del Carmen", org=org_a, created_by=admin_user
    )
    response = admin_client.patch(
        f"/api/contacts/{c.id}/",
        {"name": "María del Carmen", "description": "Updated"},
        format="json",
    )
    assert response.status_code == 200, response.data
    c.refresh_from_db()
    assert (c.first_name, c.last_name) == ("María", "del Carmen")
    assert c.source is None and c.stage is None


@pytest.mark.django_db
def test_choices_and_contact_filters_are_org_scoped(
    admin_client, org_b_client, org_a, org_b
):
    Contact.objects.create(
        first_name="Visible",
        phone="3055550199",
        source="META",
        stage="QUALIFIED",
        org=org_a,
    )
    Contact.objects.create(
        first_name="Hidden",
        phone="3055550199",
        source="META",
        stage="QUALIFIED",
        org=org_b,
    )
    response = admin_client.get("/api/contacts/?source=META&stage=QUALIFIED")
    assert [c["name"] for c in response.data["results"]] == ["Visible"]
    assert len(response.data["stages"]) == 5
    assert len(response.data["communication_channels"]) == 3
