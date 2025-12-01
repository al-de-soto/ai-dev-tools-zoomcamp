from django.test import TestCase, Client
from django.urls import reverse
from .models import TODO
from datetime import date, timedelta


class TODOModelTestCase(TestCase):
    """Test cases for the TODO model"""

    def test_create_todo(self):
        """Test creating a TODO item"""
        todo = TODO.objects.create(
            title="Test TODO",
            description="Test description",
            due_date=date.today() + timedelta(days=7)
        )
        self.assertEqual(todo.title, "Test TODO")
        self.assertEqual(todo.description, "Test description")
        self.assertFalse(todo.is_resolved)

    def test_todo_str_representation(self):
        """Test the string representation of TODO"""
        todo = TODO.objects.create(title="My TODO")
        self.assertEqual(str(todo), "My TODO")

    def test_todo_default_resolved_status(self):
        """Test that new TODOs default to unresolved"""
        todo = TODO.objects.create(title="New TODO")
        self.assertFalse(todo.is_resolved)


class TODOViewTestCase(TestCase):
    """Test cases for TODO views"""

    def setUp(self):
        """Set up test client and create test TODOs"""
        self.client = Client()
        self.todo1 = TODO.objects.create(
            title="Test TODO 1",
            description="Description 1",
            due_date=date.today() + timedelta(days=1)
        )
        self.todo2 = TODO.objects.create(
            title="Test TODO 2",
            is_resolved=True
        )

    def test_home_view(self):
        """Test the home page displays TODOs"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test TODO 1")
        self.assertContains(response, "Test TODO 2")

    def test_create_todo_view_get(self):
        """Test GET request to create TODO page"""
        response = self.client.get(reverse('create_todo'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create New TODO")

    def test_create_todo_view_post(self):
        """Test creating a TODO via POST request"""
        data = {
            'title': 'New TODO from test',
            'description': 'Test description',
            'due_date': date.today() + timedelta(days=5)
        }
        response = self.client.post(reverse('create_todo'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(TODO.objects.filter(title='New TODO from test').exists())

    def test_edit_todo_view_get(self):
        """Test GET request to edit TODO page"""
        response = self.client.get(reverse('edit_todo', args=[self.todo1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test TODO 1")

    def test_edit_todo_view_post(self):
        """Test editing a TODO via POST request"""
        data = {
            'title': 'Updated TODO',
            'description': 'Updated description',
            'due_date': ''
        }
        response = self.client.post(reverse('edit_todo', args=[self.todo1.pk]), data)
        self.assertEqual(response.status_code, 302)  # Redirect after edit
        self.todo1.refresh_from_db()
        self.assertEqual(self.todo1.title, 'Updated TODO')
        self.assertEqual(self.todo1.description, 'Updated description')

    def test_delete_todo_view_get(self):
        """Test GET request to delete confirmation page"""
        response = self.client.get(reverse('delete_todo', args=[self.todo1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Are you sure")

    def test_delete_todo_view_post(self):
        """Test deleting a TODO via POST request"""
        todo_pk = self.todo1.pk
        response = self.client.post(reverse('delete_todo', args=[todo_pk]))
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        self.assertFalse(TODO.objects.filter(pk=todo_pk).exists())

    def test_toggle_resolved_view(self):
        """Test toggling the resolved status of a TODO"""
        # Initially unresolved
        self.assertFalse(self.todo1.is_resolved)

        # Toggle to resolved
        response = self.client.get(reverse('toggle_resolved', args=[self.todo1.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect after toggle
        self.todo1.refresh_from_db()
        self.assertTrue(self.todo1.is_resolved)

        # Toggle back to unresolved
        response = self.client.get(reverse('toggle_resolved', args=[self.todo1.pk]))
        self.todo1.refresh_from_db()
        self.assertFalse(self.todo1.is_resolved)

    def test_nonexistent_todo_edit(self):
        """Test editing a non-existent TODO returns 404"""
        response = self.client.get(reverse('edit_todo', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_nonexistent_todo_delete(self):
        """Test deleting a non-existent TODO returns 404"""
        response = self.client.get(reverse('delete_todo', args=[9999]))
        self.assertEqual(response.status_code, 404)


class TODOIntegrationTestCase(TestCase):
    """Integration tests for complete TODO workflows"""

    def setUp(self):
        """Set up test client"""
        self.client = Client()

    def test_complete_todo_workflow(self):
        """Test complete workflow: create, edit, resolve, delete"""
        # Create a TODO
        create_data = {
            'title': 'Integration Test TODO',
            'description': 'Test workflow',
            'due_date': date.today() + timedelta(days=3)
        }
        response = self.client.post(reverse('create_todo'), create_data)
        self.assertEqual(response.status_code, 302)

        todo = TODO.objects.get(title='Integration Test TODO')
        self.assertFalse(todo.is_resolved)

        # Edit the TODO
        edit_data = {
            'title': 'Updated Integration Test',
            'description': 'Updated workflow',
            'due_date': date.today() + timedelta(days=5)
        }
        response = self.client.post(reverse('edit_todo', args=[todo.pk]), edit_data)
        self.assertEqual(response.status_code, 302)

        todo.refresh_from_db()
        self.assertEqual(todo.title, 'Updated Integration Test')

        # Mark as resolved
        response = self.client.get(reverse('toggle_resolved', args=[todo.pk]))
        todo.refresh_from_db()
        self.assertTrue(todo.is_resolved)

        # Delete the TODO
        response = self.client.post(reverse('delete_todo', args=[todo.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TODO.objects.filter(pk=todo.pk).exists())
