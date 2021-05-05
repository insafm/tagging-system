from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from django.contrib.auth.models import User
from .models import *

# Create your tests here.
class ModelTestCase(TestCase):
	"""This class defines the test suite for the bucketlist model."""

	def setUp(self):
		"""Define the test client and other test variables."""
		self.user = User.objects.create(first_name="first_name", last_name="last_name", email="insishere@mailinator.net", username="username1", password='Abc@12345')

	def test_model_can_create_post(self):
		"""Test the Post model can create a Post."""
		self.post = Post(description="description", images=[], tags=['a'])
		old_count = Post.objects.count()
		self.post.save()
		new_count = Post.objects.count()
		self.assertNotEqual(old_count, new_count)

	def test_model_can_create_tag(self):
		"""Test the Tag model can create a Tag."""
		self.tag = Tag(name="name")
		old_count = Tag.objects.count()
		self.tag.save()
		new_count = Tag.objects.count()
		self.assertNotEqual(old_count, new_count)

	def test_model_can_create_tagmap(self):
		"""Test the TagMap model can create a TagMap."""
		self.post = Post(description="description", images=[], tags=['a'])
		self.post.save()
		self.tag = Tag(name="name")
		self.tag.save()
		self.tagmap = TagMap(post=self.post, tag=self.tag, tag_weight=1)
		old_count = TagMap.objects.count()
		self.tagmap.save()
		new_count = TagMap.objects.count()
		self.assertNotEqual(old_count, new_count)

	def test_model_can_create_postreaction(self):
		"""Test the PostReaction model can create a PostReaction."""
		self.post = Post(description="description", images=[], tags=['a'])
		self.post.save()
		self.postreaction = PostReaction(user=self.user, post=self.post, reaction_status=1)
		old_count = PostReaction.objects.count()
		self.postreaction.save()
		new_count = PostReaction.objects.count()
		self.assertNotEqual(old_count, new_count)

	def test_model_can_create_userlikedtags(self):
		"""Test the UserLikedTags model can create a UserLikedTags."""
		self.tag = Tag(name="name")
		self.tag.save()
		self.userlikedtags = UserLikedTags(user=self.user, tag=self.tag)
		old_count = UserLikedTags.objects.count()
		self.userlikedtags.save()
		new_count = UserLikedTags.objects.count()
		self.assertNotEqual(old_count, new_count)

	def test_model_can_create_userdislikedtags(self):
		"""Test the UserDisLikedTags model can create a UserDisLikedTags."""
		self.tag = Tag(name="name")
		self.tag.save()
		self.userdislikedtags = UserDisLikedTags(user=self.user, tag=self.tag)
		old_count = UserDisLikedTags.objects.count()
		self.userdislikedtags.save()
		new_count = UserDisLikedTags.objects.count()
		self.assertNotEqual(old_count, new_count)



class ViewTestCase(TestCase):
	"""Test suite for the api views."""

	def setUp(self):
		"""Define the test client and other test variables."""
		self.client = APIClient()
		self.initialize_user_data = {
			"username": "b",
			"email": "b@test.com",
			"first_name": "b",
			"last_name": "b",
			"password": "b"
		}
		self.response = self.client.post(
										reverse('post:users_list'),
										self.initialize_user_data,
										format="json"
										)
		response_json = self.response.json()
		self.api_token = response_json['data']['token']

	def test_api_can_initialize_user_data(self):
		"""Test the api has initialize user account."""
		# print(self.response.json())
		self.assertEqual(self.response.status_code, status.HTTP_200_OK)
		self.assertIn("data", self.response.json())
		self.assertIn("token", self.response.json()["data"])

	def test_api_can_list_post(self):
		"""Test the api list posts."""
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.api_token)
		response = self.client.get(
			reverse('post:posts_list'),
			format="json"
			)
		self.assertEqual(response.status_code, status.HTTP_200_OK)