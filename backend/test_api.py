from apps.messaging.views import MessageViewSet
from apps.authentication.models import User
from django.test import RequestFactory
from rest_framework.test import force_authenticate

factory = RequestFactory()
request = factory.get('/')
view = MessageViewSet.as_view({'get': 'conversations'})

for u in User.objects.all():
    force_authenticate(request, user=u)
    r = view(request)
    if r.data:
        print(f"User {u.id}: {r.data}")
