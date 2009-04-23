from django.conf.urls.defaults import *
from models import User

urlpatterns = patterns('django.views.generic.list_detail',
    (r'^/*$',               'object_list', {'queryset': User.objects.all(), }),
)
