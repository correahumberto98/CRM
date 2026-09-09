"""Issue a development sign-in link from an explicitly opted-in local shell."""

import os
import secrets
from datetime import timedelta
from urllib.parse import urlsplit

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from common.models import MagicLinkToken, User


class Command(BaseCommand):
    help = "Create a single-use local development login link for an existing user."

    def add_arguments(self, parser):
        parser.add_argument("--email", default="admin@example.com")

    def handle(self, *args, **options):
        if not settings.DEBUG or os.environ.get("CRM_LOCAL_LOGIN") != "1":
            raise CommandError("Local login requires DEBUG=True and CRM_LOCAL_LOGIN=1.")
        origin = settings.FRONTEND_URL.rstrip("/")
        parsed = urlsplit(origin)
        if (
            parsed.scheme != "http"
            or parsed.hostname not in ("localhost", "127.0.0.1", "::1")
            or parsed.username
            or parsed.password
            or parsed.path
            or parsed.query
            or parsed.fragment
        ):
            raise CommandError("Local login requires a loopback HTTP FRONTEND_URL.")
        email = options["email"].strip().lower()
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if not user:
            raise CommandError("No active local user with that email exists.")
        with transaction.atomic():
            MagicLinkToken.objects.filter(email=user.email, is_used=False).update(
                is_used=True
            )
            token = MagicLinkToken.objects.create(
                email=user.email,
                token=secrets.token_hex(32),
                expires_at=timezone.now() + timedelta(minutes=2),
                delivery=MagicLinkToken.DELIVERY_LINK,
                ip_address="127.0.0.1",
            )
        self.stdout.write(f"{origin}/login/verify?token={token.token}")
