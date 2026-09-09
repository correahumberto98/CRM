from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings
from django.utils import timezone

from common.models import MagicLinkToken, User

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "debug,optin,url",
    [
        (False, "1", "http://localhost:5173"),
        (True, "0", "http://localhost:5173"),
        (True, "1", "https://crm.example.com"),
    ],
)
def test_local_login_disabled_outside_opted_in_development(debug, optin, url):
    with (
        override_settings(DEBUG=debug, FRONTEND_URL=url),
        patch.dict("os.environ", {"CRM_LOCAL_LOGIN": optin}),
    ):
        with pytest.raises(CommandError):
            call_command("local_login_link", stdout=StringIO())
    assert not MagicLinkToken.objects.exists()


def test_local_link_uses_existing_active_account_and_short_expiry():
    User.objects.create(email="admin@example.com", is_active=True)
    with (
        override_settings(DEBUG=True, FRONTEND_URL="http://localhost:5173"),
        patch.dict("os.environ", {"CRM_LOCAL_LOGIN": "1"}),
    ):
        output = StringIO()
        call_command("local_login_link", stdout=output)
        token = MagicLinkToken.objects.get()
        assert (
            output.getvalue().strip()
            == f"http://localhost:5173/login/verify?token={token.token}"
        )
        assert 0 < (token.expires_at - timezone.now()).total_seconds() <= 120
        call_command("local_login_link", stdout=StringIO())
        token.refresh_from_db()
        assert token.is_used
        with pytest.raises(CommandError):
            call_command(
                "local_login_link", email="missing@example.com", stdout=StringIO()
            )
        assert User.objects.count() == 1
