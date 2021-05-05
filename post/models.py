from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
	description = models.CharField(max_length=255)
	images = JSONField(default=list, blank=True, null=True)
	tags = JSONField(default=list, blank=True, null=True)
	likes = models.IntegerField(blank=True, null=True, default=0)
	dislikes = models.IntegerField(blank=True, null=True, default=0)
	created = models.DateTimeField(default=timezone.now)

class Tag(models.Model):
	name = models.CharField(max_length=255, unique=True)
	created = models.DateTimeField(default=timezone.now)
	
	def __str__(self):
		return self.name


class TagMap(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
	tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
	tag_weight = models.IntegerField(blank=True, null=True, default=1)
	created = models.DateTimeField(default=timezone.now)

class PostReaction(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
	reaction_status = models.SmallIntegerField(blank=True, null=True, default=0) #NO REACTION:0, LIKE: 1, DISLIKE:-1
	created = models.DateTimeField(default=timezone.now)

class UserLikedTags(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
	created = models.DateTimeField(default=timezone.now)

class UserDisLikedTags(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
	created = models.DateTimeField(default=timezone.now)