from django.contrib import messages
from datetime import timezone
from django.conf import settings

import pprint
pp = pprint.pprint

def custom_send_mail(data={}):
	from django.core.mail import send_mail
	print("Sending mail...", data)
	
	if "from_email" not in data:
		data['from_email'] = settings.EMAIL_HOST_USER
	
	send = send_mail(**data)
	if send:
		return True

	return False