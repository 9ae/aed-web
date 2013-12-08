# Create your views here.

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.utils import simplejson
from django.core import serializers

import models

# from perform.helpers import cereal

def index(request):
	return HttpResponse("Hello")

def actions_list(request,paradigm_id):
	pid = int(paradigm_id)
	actions = models.Action.objects.filter(paradigm_id__exact=pid)
	s = serializers.serialize("json", actions)
	return HttpResponse(s, content_type="application/json")
	