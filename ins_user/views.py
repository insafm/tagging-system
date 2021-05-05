from django.shortcuts import render
from django.views import View
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from datetime import timezone
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.base import TemplateView

from django.contrib.auth.models import Group, Permission

import pprint
pp = pprint.pprint

from .signals import post_create_user_signal

# Front page with login
class InsHomePage(LoginView):
	template_name = 'home.html'
	redirect_authenticated_user = True

# Logout
class InsLogoutView(LogoutView, InsHomePage):
	template_name = 'home.html'
	next_page = 'index'