import django.dispatch

# Signal for doing something after user creation START
post_create_user_signal = django.dispatch.Signal(providing_args=['user', 'request'])
# Signal for doing something after user creation END