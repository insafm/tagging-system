from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.views import View
from django.utils.translation import ugettext as _
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required

from .forms import AddPostForm
from .models import *
from .tables import PostTable
# Create your views here.

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class AddPost(View):
	template = 'form-wrapper.html'
	context = {}
	context['label'] = _('Import File')
	def get(self, request, *args, **kwargs):
		initial = {}
		form = AddPostForm(request.POST or None, request.FILES or None, initial=initial)

		self.context['title']       = _("Upload Files")
		self.context["files"] = True
		self.context['form'] = form
		self.context['form_media'] = form.media

		return render(request, self.template, self.context)


	def post(self, request, *args, **kwargs):
		form = AddPostForm(request.POST or None,request.FILES or None,initial={})
		if form.is_valid():
			
			post = form.save()

			image_list = request.FILES.getlist('image')
			images_path = []
			fs = FileSystemStorage()
			for image in image_list:
				upload_path = 'post/'+image.name
				filename = fs.save(upload_path, image)
				images_path.append(settings.MEDIA_URL+upload_path)
			
			post.images = images_path
			post.save()

			print(images_path)

			messages.add_message(request, messages.INFO, _("Post updated."))

			return redirect('post:add_post')

		else:
			# redirect response
			return redirect('post:add_post')

		return redirect('post:add_post')

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class Posts(View):
	"""List the posts, with 10 posts per page."""
	model = Post
	table_class = PostTable
	template_name = 'table.html'
	def get(self, request, *args, **kwargs):
		queryset = self.model.objects.all()
		table = self.table_class(queryset)
		table.paginate(page=request.GET.get("page", 1), per_page=10)
		return render(request, self.template_name, {"table": table, "title": "Posts"})


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class Reset(View):
	context = {}
	def get(self, request, *args, **kwargs):
		

		Post.objects.all().delete()
		Tag.objects.all().delete()
		TagMap.objects.all().delete()
		PostReaction.objects.all().delete()
		UserLikedTags.objects.all().delete()
		UserDisLikedTags.objects.all().delete()
		
		messages.add_message(request, messages.SUCCESS, _("Reset success."))
		return redirect('post:add_post')