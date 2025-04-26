"""
Tests for the atomic server views (`begin` and `rollback`).

These tests ensure that the atomic views correctly manage database transactions,
allowing state changes within a `begin`/`rollback` block to be isolated and
reverted.
"""

from django.test import TestCase

from tasks.models import Task


class TestAtomicView(TestCase):
    """
    Tests the functionality of the `/atomic/begin/` and `/atomic/rollback/` endpoints.
    """

    def setUp(self) -> None:
        """Creates an initial Task object before each test."""
        Task.objects.create(title="Task 1")

    def test_setup_teardown(self) -> None:
        """
        Tests the core begin-rollback cycle.

        Verifies that:
        1. Calling `/atomic/begin/` is successful.
        2. Database changes made after `begin` are visible.
        3. Calling `/atomic/rollback/` is successful.
        4. Database changes made after `begin` are reverted after `rollback`.
        """
        # Start atomic context
        response = self.client.get("/atomic/begin/")
        self.assertEqual(response.status_code, 204)

        # Create a task within the atomic context
        Task.objects.create(title="Task 2")
        self.assertEqual(Task.objects.count(), 2)

        # Rollback the transaction
        response = self.client.get("/atomic/rollback/")
        self.assertEqual(response.status_code, 204)

        # Verify the task created within the context was rolled back
        self.assertEqual(Task.objects.count(), 1)
