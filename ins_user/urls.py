from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
 	path('logout/', views.InsLogoutView.as_view(), name='ins_logout'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)