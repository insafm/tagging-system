from django.test import TestCase

from django.contrib.auth.models import User
from ins_user.util import custom_send_mail

# Create your tests here.

class ApiTestCaseSendMail(TestCase):
	def setUp(self):
		self.user = User.objects.create(first_name="first_name", last_name="last_name", email="insishere@mailinator.net", username="username1", password='Abc@12345')

	def test_create_user_profile(self):
		"""Test the customer or user creation model can create user objects."""
		self.assertEqual(self.user.username, "username1")