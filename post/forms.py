from django import forms
from django.forms import ModelForm, Textarea
from django.utils.translation import ugettext as _

from django.core.exceptions import ValidationError

from .models import Post, Tag, TagMap

class AddPostForm(forms.Form):

	image = forms.FileField(label=_("Images"), widget=forms.ClearableFileInput(attrs={'multiple': True}))
	description = forms.CharField(widget=forms.Textarea(attrs={'rows': '3', 'cols': '80'}), help_text='Post description. Required.')
	tags = forms.CharField(widget=forms.TextInput(attrs={'size': '80'}), help_text='Post Tags, Enter multiple tags by seperating with comma. Each tags has curresponding weight by order.')

	def __init__(self, *args, **kwargs):
		super(AddPostForm, self).__init__(*args, **kwargs)
		pass

	def clean(self):
		image = self.cleaned_data.get('image')
		if image and image.size > 5000000:
			raise forms.ValidationError("Maximum upload size is 5MB.")

		return self.cleaned_data

	def save(self):
		description = self.cleaned_data['description']
		tags = list(self.cleaned_data['tags'].split(","))

		# create post
		post = Post()
		post.description = description
		post.tags = tags
		post.save()

		tags_obj = []
		tag_map_obj = []
		for x in tags:
			tags_obj.append(Tag(name=x))

		tag_created = None
		if tags_obj:
			tag_created = Tag.objects.bulk_create(tags_obj, ignore_conflicts=True)
			print("tag_created::: ", tag_created)

		tag_weight = 1
		for x in tags:
			tag = Tag.objects.get(name=x)
			if tag:
				tag_map_obj.append(TagMap(post=post, tag=tag, tag_weight=tag_weight))
				tag_weight += 1

		if tag_map_obj:
			TagMap.objects.bulk_create(tag_map_obj)

		return post