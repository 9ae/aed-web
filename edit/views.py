# Create your views here.

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.utils import simplejson
from django.core import serializers

import models
from decadence import json_encode_decimal

# from perform.helpers import cereal

def index(request):
	return HttpResponse("Hello")

def actions_list(request,paradigm_id):
	pid = int(paradigm_id)
	actions = models.Action.objects.filter(paradigm_id__exact=pid)
	s = serializers.serialize("json", actions)
	return HttpResponse(s, content_type="application/json")

def events_list(request,protocol_id):
	pid = int(protocol_id)
	events = models.Event.objects.filter(protocol_id__exact=pid)
	s = serializers.serialize("json", events)
	return HttpResponse(s, content_type="application/json")

def intervals_list(request,protocol_id):
	pid = int(protocol_id)
	context = request.GET.get('context',None)
	if context=='graph':
		intervals = models.Interval.objects.filter(protocol_id__exact=pid).order_by('order').values('name','duration','color')
		ilist = list(intervals)
		s = simplejson.dumps(ilist,default=json_encode_decimal)
		return HttpResponse(s, content_type="application/json")
	else:
		intervals = models.Interval.objects.filter(protocol_id__exact=pid).order_by('order')
		s = serializers.serialize("json", intervals)
		return HttpResponse(s, content_type="application/json")

def intervals_listview(request,protocol_id):
	pid = int(protocol_id)
	protocol = models.Protocol.objects.get(id=pid)
	intervals = protocol.intervals()
	content = {'intervals':intervals}
	return render(request,'intervals.html',content)