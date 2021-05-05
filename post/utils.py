from rest_framework import status
from rest_framework.views import exception_handler

from .models import Post, PostReaction, UserLikedTags, UserDisLikedTags, Tag

def apiSuccess(data=None, status_code=status.HTTP_200_OK):
	'''
		API success reponse formatter
	'''
	status_text = "success"
	if "error" in data:
		status_text = "fail"

	defaultsData = {}
	return {
		"status" : status_text,
		"data": (defaultsData if data is None else data)
	}

def apiError(apiexception):
	'''
		Error formatter for non ApiView errors
	'''
	print("IN erroror----------------", apiexception)
	return {
		"status_code":apiexception.status_code if hasattr(apiexception, "status_code") else status.HTTP_400_BAD_REQUEST,
		"error":{
			"type":apiexception.default_error_type if hasattr(apiexception, "default_error_type") else "exception",
			"detail": apiexception.detail if hasattr(apiexception, "detail") else str(apiexception),
		}
	}

def custom_exception_handler(exc, context):
	print("IN custom_exception_handler-------------")
	# Call REST framework's default exception handler first, 
	# to get the standard error response.
	response = exception_handler(exc, context)
	# Now update response data with custom data.
	if response is not None:
		res = {
			"status": "fail",
			"error": response.data
		}
		response.data = res

	return response


# Check post_id valid
def is_valid_post_id(post_id):
	exists = Post.objects.filter(pk=post_id).exists()
	return exists

# Get reaction_status list
def get_reaction_status_list():
	reaction_status = [-1, 0, 1]
	return reaction_status

# Check reaction_status valid
def is_valid_reaction_status(reaction_status):
	valid_status = get_reaction_status_list()
	if reaction_status in valid_status:
		return True
	return False

# Check ALready reacted.
def is_valid_reaction(user, post_id, reaction_status):
	exists = PostReaction.objects.filter(user=user, post_id=post_id, reaction_status=reaction_status).exists()
	if exists:
		return False
	return True

# React user to the post by id
def user_react_post(user, post_id, reaction_status):
	# 1. Add and Remove to PostReaction
	# 2. Add to UserLikedTags if liked
	# 3. Remove from UserLikedTags if disliked.
	# 4. Add to UserDisLikedTags if disliked
	# 5. Remove from UserDisLikedTags if liked.
	# 6. Update Post likes/dislikes count.

	# Add and Remove to PostReaction
	reacted = PostReaction.objects.filter(user=user, post_id=post_id).values_list('reaction_status', flat=True).first()
	if reacted:
		PostReaction.objects.filter(user=user, post_id=post_id).delete()
	post_reaction = PostReaction.objects.create(user=user, post_id=post_id, reaction_status=reaction_status)
	post_tags = post_reaction.post.tags

	print("post_reaction: ", post_reaction)
	print("post: ", post_reaction.post.__dict__)
	print("post_tags: ", post_tags)

	# If Liked?
	if reaction_status == 1:

		# Update Post likes/dislikes count.
		if reacted and reacted == -1:
			print("reacted::: ", reacted)
			post_reaction.post.dislikes -= 1
		post_reaction.post.likes += 1
		post_reaction.post.save()

		# Remove from UserDisLikedTags if liked.
		UserDisLikedTags.objects.filter(user=user, tag__name__in=post_tags).delete()

		# Add to UserLikedTags if liked
		liked_tags = UserLikedTags.objects.filter(user=user).values_list('tag__name').all()
		print("liked_tags: ", liked_tags)
		for post_tag in post_tags:
			if post_tag not in liked_tags:
				tag = Tag.objects.get(name=post_tag)
				if tag:
					UserLikedTags.objects.create(user=user, tag=tag)

	# If disliked?
	elif reaction_status == -1:

		# Update Post likes/dislikes count.
		if reacted and reacted == 1:
			print("reacted::: ", reacted)
			post_reaction.post.likes -= 1
		post_reaction.post.dislikes += 1
		post_reaction.post.save()

		# Remove from UserLikedTags if liked.
		UserLikedTags.objects.filter(user=user, tag__name__in=post_tags).delete()

		# Add to UserDisLikedTags if disliked
		disliked_tags = UserDisLikedTags.objects.filter(user=user).values_list('tag__name').all()
		print("disliked_tags: ", disliked_tags)
		for post_tag in post_tags:
			if post_tag not in disliked_tags:
				tag = Tag.objects.get(name=post_tag)
				if tag:
					UserDisLikedTags.objects.create(user=user, tag=tag)
	
	# If reaction cleared?
	elif reaction_status == 0:

		# Update Post likes/dislikes count.
		if reacted and reacted == 1:
			print("reacted::: ", reacted)
			post_reaction.post.likes -= 1
		elif reacted and reacted == -1:
			print("reacted::: ", reacted)
			post_reaction.post.dislikes -= 1

		post_reaction.post.save()

		# Remove from UserLikedTags if liked.
		UserLikedTags.objects.filter(user=user, tag__name__in=post_tags).delete()
		UserDisLikedTags.objects.filter(user=user, tag__name__in=post_tags).delete()


	return True

def get_reaction_status_text(reaction_status):
	status_text = "NOT REACTED"
	if reaction_status == 1:
		status_text = "LIKED"
	elif reaction_status == -1:
		status_text = "DISLIKED"
	return status_text