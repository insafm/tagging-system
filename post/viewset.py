import traceback
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, authentication, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from .models import Post, PostReaction, UserLikedTags, UserDisLikedTags, TagMap
from .utils import *

class PostViewSet(viewsets.ViewSet):
	"""
	A simple ViewSet for post.
	"""
	authentication_classes = [authentication.TokenAuthentication]
	permission_classes = (permissions.IsAuthenticated,)
	def list(self, request):
		user = request.user
		liked_tags_list = tuple(list(UserLikedTags.objects.filter(user=user).values_list('tag__name', flat=True)))
		disliked_tags_list = tuple(list(UserDisLikedTags.objects.filter(user=user).values_list('tag__name', flat=True)))

		print("request.user: ", request.user)
		print("liked_tags_list: ", liked_tags_list)
		print("disliked_tags_list: ", disliked_tags_list)

		if len(liked_tags_list) == 1:
			liked_tags_list = str(tuple(liked_tags_list))[:-2]+")"
		if len(disliked_tags_list) == 1:
			disliked_tags_list = str(tuple(disliked_tags_list))[:-2]+")"

		row_qry = """
			SELECT p.id, p.images, p.description, p.likes, pr.reaction_status, p.dislikes, p.created
			FROM post_post p
			JOIN post_tagmap tm on tm.post_id = p.id
			JOIN post_tag t on tm.tag_id = t.id
			LEFT JOIN post_postreaction pr on (pr.post_id = p.id AND pr.user_id = {user_id})
			JOIN (
				SELECT post_id, count(tag_id) as tag_count
				FROM post_tagmap
				GROUP BY post_id
			) counts on counts.post_id = p.id
		""".format(user_id=user.id)

		if liked_tags_list or disliked_tags_list:
			row_qry += " WHERE "

		if liked_tags_list:
			row_qry += """
				t.name in {liked_tags_list}
			""".format(liked_tags_list=liked_tags_list)
		
		if liked_tags_list and disliked_tags_list:
			row_qry += " AND "

		if disliked_tags_list:
			row_qry += """
				t.name NOT IN {disliked_tags_list}
			""".format(disliked_tags_list=disliked_tags_list)

		row_qry += "ORDER BY tm.tag_weight ASC, tag_count DESC, p.id ASC, t.name ASC"

		print("row_qry: ", row_qry)
		data = Post.objects.raw(row_qry)

		return_data = {}
		for d in data:
			if d.id not in return_data:
				return_data[d.id] = {}
				return_data[d.id]['images'] = d.images
				return_data[d.id]['description'] = d.description
				return_data[d.id]['reaction_status'] = get_reaction_status_text(d.reaction_status)
				return_data[d.id]['likes'] = d.likes
				return_data[d.id]['dislikes'] = d.dislikes
				return_data[d.id]['created'] = d.created

		# least priority posts
		least_priority_data = {}
		least_priority_posts = PostReaction.objects.filter(user=user, reaction_status=-1).all()
		for reaction in least_priority_posts:
			if reaction.post.id not in least_priority_data:
				least_priority_data[reaction.post.id] = {}
				least_priority_data[reaction.post.id]['images'] = reaction.post.images
				least_priority_data[reaction.post.id]['description'] = reaction.post.description
				least_priority_data[reaction.post.id]['reaction_status'] = get_reaction_status_text(reaction.reaction_status)
				least_priority_data[reaction.post.id]['likes'] = reaction.post.likes
				least_priority_data[reaction.post.id]['dislikes'] = reaction.post.dislikes
				least_priority_data[reaction.post.id]['created'] = reaction.post.created

		# medium priority posts 
		medium_priority_posts = Post.objects.filter(~Q(pk__in=list(return_data.keys())+list(least_priority_data.keys()))).all()
		for d in medium_priority_posts:
			if d.id not in return_data:
				return_data[d.id] = {}
				return_data[d.id]['images'] = d.images
				return_data[d.id]['description'] = d.description
				return_data[d.id]['reaction_status'] = get_reaction_status_text(0)
				return_data[d.id]['likes'] = d.likes
				return_data[d.id]['dislikes'] = d.dislikes
				return_data[d.id]['created'] = d.created

		# Combine disliked post to data
		return_data.update(least_priority_data)

		return Response(apiSuccess(return_data), status=status.HTTP_200_OK)


class UserViewSet(viewsets.ViewSet):
	"""
	ViewSet for create users.
	"""
	def create(self, request):
		try:
			if request.data:
				return_data = {}
				user = User.objects.create(
					username=request.data['username'],
					email=request.data['email'],
					first_name=request.data['first_name'],
					last_name=request.data['last_name']
					)
				user.set_password(request.data['password'])
				user.save()

				# Create token for your user.
				token, created = Token.objects.get_or_create(user=user)
				return_data["token"] = token.key
				return_data["username"] = user.username
				return Response(apiSuccess(return_data), status=status.HTTP_200_OK)
			else:
				return Response(apiSuccess({'error': 'Empty data'}), status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response(apiError(e))


class ReactionViewSet(viewsets.ViewSet):
	"""
	A simple ViewSet for reactions.
	"""
	authentication_classes = [authentication.TokenAuthentication]
	permission_classes = (permissions.IsAuthenticated,)
	def create(self, request):
		try:
			if request.data:
				user = request.user
				
				post_id = request.data['post_id'] if "post_id" in request.data else None
				reaction_status = request.data['reaction_status'] if "reaction_status" in request.data else None

				if not post_id or not reaction_status:
					return Response(apiSuccess({'error': 'Invalid data'}), status=status.HTTP_400_BAD_REQUEST)

				# Validations need to be done:
				# 1. Check post_id, reaction_status are valid
				# 2. Check ALready reacted.

				if not is_valid_post_id(post_id):
					return Response(apiSuccess({'error': 'Invalid post id'}), status=status.HTTP_400_BAD_REQUEST)

				if not is_valid_reaction_status(reaction_status):
					return Response(apiSuccess({'error': 'Invalid reaction'}), status=status.HTTP_400_BAD_REQUEST)

				if not is_valid_reaction(user=user, post_id=post_id, reaction_status=reaction_status):
					return Response(apiSuccess({'error': 'Already reacted'}), status=status.HTTP_400_BAD_REQUEST)
				
				# React the post
				reacted = user_react_post(user=user, post_id=post_id, reaction_status=reaction_status)
				if reacted:
					return_data = {}
					return_data['message'] = 'Successfully reacted'
					return Response(apiSuccess(return_data), status=status.HTTP_200_OK)
				else:
					return Response(apiSuccess({'error': 'Reacting on post was failed'}), status=status.HTTP_400_BAD_REQUEST)
			else:
				return Response(apiSuccess({'error': 'Invalid data'}), status=status.HTTP_400_BAD_REQUEST)

		except Exception as e:
			print(e)
			traceback.print_exc()
			return Response(apiError(e))

	# API that returns a list of all the users who liked a post
	def list(self, request):
		try:
			if request.data:
				return_data = {}

				user = request.user
				post_id = request.data['post_id'] if "post_id" in request.data else None

				if not post_id:
					return_data['error'] = 'Invalid data'
					return Response(apiSuccess(return_data), status=status.HTTP_400_BAD_REQUEST)

				if not is_valid_post_id(post_id):
					return_data['error'] = 'Invalid post id'
					return Response(apiSuccess(return_data), status=status.HTTP_400_BAD_REQUEST)

				liked_users = PostReaction.objects.filter(post_id=post_id, reaction_status=1).values('user_id', 'user__username', 'created').all()
				i = 0
				for user in liked_users:
					return_data[i] = {}
					return_data[i]['uid'] = user['user_id']
					return_data[i]['username'] = user['user__username']
					return_data[i]['liked'] = user['created']
					i += 1

				return Response(apiSuccess(return_data), status=status.HTTP_200_OK)
		except Exception as e:
			print(e)
			traceback.print_exc()
			return Response(apiError(e))