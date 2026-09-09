import pytest

from contacts.models import Contact

pytestmark = pytest.mark.django_db


def test_sort_applies_before_pagination_and_stays_org_scoped(
    admin_client, org_a, org_b
):
    for name in ["Zulu", "alpha", "Bravo"]:
        Contact.objects.create(first_name=name, org=org_a)
    Contact.objects.create(first_name="A hidden contact", org=org_b)
    first = admin_client.get("/api/contacts/?sort=name&direction=asc&limit=1").data
    second = admin_client.get(
        "/api/contacts/?sort=name&direction=asc&limit=1&offset=1"
    ).data
    last = admin_client.get("/api/contacts/?sort=name&direction=desc&limit=1").data
    assert first["count"] == 3
    assert first["results"][0]["name"] == "alpha"
    assert second["results"][0]["name"] == "Bravo"
    assert last["results"][0]["name"] == "Zulu"


@pytest.mark.parametrize(
    "key",
    [
        "phone",
        "email",
        "source_label",
        "stage_label",
        "owner",
        "account",
        "address_line",
        "city",
        "postcode",
        "state",
        "preferred_communication_channel_label",
        "description",
        "is_active",
        "do_not_call",
        "created_at",
        "updated_at",
        "not_an_allowed_field",
    ],
)
def test_sort_columns_are_valid_and_do_not_duplicate_contacts(admin_client, org_a, key):
    Contact.objects.create(first_name="One", org=org_a, stage="LEAD")
    Contact.objects.create(first_name="Two", org=org_a, stage="QUALIFIED")
    response = admin_client.get(f"/api/contacts/?sort={key}&direction=desc")
    assert response.status_code == 200, response.data
    assert response.data["count"] == 2
    assert len({row["id"] for row in response.data["results"]}) == 2
