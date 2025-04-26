"""
Provides the AtomicSession utility for managing database transactions
across multiple databases, primarily for ensuring clean state between
requests in the atomic server context.
"""

from django.db import DEFAULT_DB_ALIAS, connections, transaction
from django.db.transaction import Atomic


class AtomicSession:
    """
    Manages atomic transaction blocks for configured databases.

    This class provides methods to enter and exit atomic blocks, effectively
    wrapping operations (like handling a request) within transactions that can be
    rolled back.
    """

    # Stores the active Atomic instances, keyed by database alias.
    scope: dict[str, Atomic] | None = None

    @classmethod
    def databases_names(cls, include_mirrors: bool = True) -> list[str]:
        """Return a list of database aliases to manage transactions for."""
        # Only consider allowed database aliases, including mirrors or not.
        return [
            alias
            for alias in connections
            if alias in {DEFAULT_DB_ALIAS}
            and (
                include_mirrors
                or not connections[alias].settings_dict["TEST"]["MIRROR"]
            )
        ]

    @classmethod
    def enter_atomics(cls) -> None:
        """Starts atomic transaction blocks for each relevant database."""
        atomics = {}
        for db_name in cls.databases_names():
            atomic: Atomic = transaction.atomic(using=db_name)
            atomic._from_testcase = True  # type: ignore[attr-defined]
            atomic.__enter__()
            atomics[db_name] = atomic
        cls.scope = atomics

    @classmethod
    def rollback_atomics(cls) -> None:
        """Rolls back all active atomic transaction blocks."""
        if cls.scope is None:
            raise ValueError("Not inside an atomic context")

        for db_name in reversed(cls.databases_names()):
            # Ensure the transaction is marked for rollback before exiting.
            transaction.set_rollback(True, using=db_name)
            cls.scope[db_name].__exit__(None, None, None)

    @classmethod
    def close_all(cls) -> None:
        """Closes all database connections."""
        connections.close_all()
