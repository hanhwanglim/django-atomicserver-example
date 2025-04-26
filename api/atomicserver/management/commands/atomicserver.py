"""
Atomic server management command

This command runs a modified Django development server that wraps every request
within a database transaction. This ensures that any database changes made during
a request are rolled back at the end of the request, providing a clean state
for subsequent requests. This is particularly useful for end-to-end (E2E) testing
scenarios where tests need to run against a predictable database state.
"""

from typing import Any

from django.core.servers.basehttp import (
    WSGIRequestHandler,
    get_internal_wsgi_application,
)
from django.core.servers.basehttp import WSGIServer
from django.core.management import CommandError, CommandParser  # type: ignore[attr-defined]

from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.core.signals import request_started, request_finished
from django.db import close_old_connections
from django.test import override_settings

from atomicserver.atomic import AtomicSession

DEFAULT_ADDRPORT = "127.0.0.1:8000"


class Command(BaseCommand):
    """
    Defines the `atomicserver` management command.

    This command starts a WSGI server similar to Django's `runserver`, but
    with added logic to manage atomic transactions for each request using
    the `AtomicSession` utility.
    """

    help = "Runs an atomic server"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--addrport",
            default=DEFAULT_ADDRPORT,
            help="Port number or ipaddr:port to run the server on.",
        )
        parser.add_argument(
            "--collectstatic",
            action="store_true",
            help="Collects static files from static folder.",
        )
        parser.add_argument(
            "--ipv6",
            "-6",
            action="store_true",
            dest="use_ipv6",
            help="Start server on IPv6 address.",
        )

    def handle(self, *args: str, **options: Any) -> None:
        """Handles the execution of the atomicserver command."""
        if options["collectstatic"]:
            call_command("collectstatic", interactive=False)

        try:
            addr_str, port_str = options["addrport"].split(":")
            addr: str = addr_str
            port: int = int(port_str)
        except ValueError:
            raise CommandError("Not a valid address:port")

        # Modify database settings in-memory to disable autocommit.
        # This is crucial for the atomic behavior, as it allows transactions
        # to span the entire request and be rolled back later.
        database_settings = settings.DATABASES
        for db_settings in database_settings.values():
            db_settings["AUTO_COMMIT"] = False  # disabling autocommit allows rollback
        override_settings(DATABASES=database_settings)

        httpd = WSGIServer(
            (addr, port), WSGIRequestHandler, ipv6=options.get("use_ipv6", False)
        )
        httpd.set_app(get_internal_wsgi_application())
        self.stdout.write(f"Starting atomic server on {options['addrport']}.")

        AtomicSession.enter_atomics()

        # Disconnect Django's default request signals that close database connections.
        # If connections are closed prematurely, we lose the ability to roll back
        # the transaction associated with the request.
        request_started.disconnect(close_old_connections)
        request_finished.disconnect(close_old_connections)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            self.stdout.write("\nShutting down E2E server.")
        finally:
            AtomicSession.rollback_atomics()
            AtomicSession.close_all()
