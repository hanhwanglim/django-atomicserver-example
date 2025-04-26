from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Task


class TaskModelTests(APITestCase):
    def test_task_creation(self) -> None:
        """
        Ensure we can create a new task object.
        """
        task_title = "Test Task Item"
        task = Task.objects.create(title=task_title)
        self.assertEqual(task.title, task_title)
        self.assertFalse(task.completed)
        self.assertEqual(str(task), task_title)


class TaskAPITests(APITestCase):
    def setUp(self) -> None:
        self.task1 = Task.objects.create(title="Task 1", completed=False)
        self.task2 = Task.objects.create(title="Task 2", completed=True)
        self.list_url = reverse("task-list")
        self.detail_url = lambda pk: reverse("task-detail", args=[pk])

    def test_list_tasks(self) -> None:
        """
        Ensure we can list all task items.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["title"], self.task1.title)
        self.assertEqual(response.data[1]["title"], self.task2.title)

    def test_create_task(self) -> None:
        """
        Ensure we can create a new task item via the API.
        """
        data = {"title": "New Task 3", "completed": False}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 3)
        new_task = Task.objects.get(pk=response.data["id"])
        self.assertEqual(new_task.title, "New Task 3")

    def test_retrieve_task(self) -> None:
        """
        Ensure we can retrieve a single task item by its id.
        """
        response = self.client.get(self.detail_url(self.task1.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.task1.title)

    def test_update_task(self) -> None:
        """
        Ensure we can update a task item.
        """
        data = {"title": "Updated Task 1", "completed": True}
        response = self.client.put(self.detail_url(self.task1.pk), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, "Updated Task 1")
        self.assertTrue(self.task1.completed)

    def test_partial_update_task(self) -> None:
        """
        Ensure we can partially update a task item (PATCH).
        """
        data = {"completed": True}
        response = self.client.patch(
            self.detail_url(self.task1.pk), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, "Task 1")
        self.assertTrue(self.task1.completed)

    def test_delete_task(self) -> None:
        """
        Ensure we can delete a task item.
        """
        response = self.client.delete(self.detail_url(self.task1.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 1)
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(pk=self.task1.pk)

    def test_invalid_task_create(self) -> None:
        """
        Ensure creating a task without a title fails.
        """
        data = {"completed": False}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_retrieve_non_existent_task(self) -> None:
        """
        Ensure retrieving a non-existent task returns 404.
        """
        non_existent_pk = 999
        response = self.client.get(self.detail_url(non_existent_pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
