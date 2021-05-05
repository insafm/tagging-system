import django_tables2 as tables
import itertools
from django_tables2.utils import A

from .models import Post

class PostTable(tables.Table):
	counter = tables.Column(verbose_name="#", empty_values=(), orderable=False)
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def render_counter(self):
		self.row_counter = getattr(self, 'row_counter', itertools.count(start=self.page.start_index()))
		return next(self.row_counter)

	class Meta:
		model = Post
		template_name = "django_tables2/bootstrap-responsive.html"
		fields = ("description", "likes", "dislikes", "created")
		sequence = ('counter', '...')