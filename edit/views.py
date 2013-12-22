# Create your views here.

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.utils import simplejson
from django.core import serializers

import models
from decadence import json_encode_decimal
from perform.helpers import cereal

# from perform.helpers import cereal

def index(request):
	return HttpResponse("Hello")

def get_protocol(request,protocol_id):
	pid = int(protocol_id)
	protocol = models.Protocol.objects.get(id=pid)
	ps = cereal(protocol)
	context = request.GET.get('context',None)
	if context=='graph':
		actions = models.Action.objects.filter(paradigm_id__exact=protocol.paradigm).values('type','color')
		alist = list(actions)
		astr = simplejson.dumps(alist)
		events = models.Event.objects.filter(protocol_id__exact=pid).values('name','color')
		elist = list(events)
		estr = simplejson.dumps(elist)
		intervals = models.Interval.objects.filter(protocol_id__exact=pid).order_by('order').values('name','duration','color')
		ilist = list(intervals)
		istr = simplejson.dumps(ilist,default=json_encode_decimal)
		result_str = '{"protocol":'+ps+',"actions":'+astr+',"events":'+estr+',"intervals":'+istr+'}'
		return HttpResponse(result_str, content_type="application/json")
	else:
		return HttpResponse(ps, content_type="application/json")

def actions_list(request,paradigm_id):
	pid = int(paradigm_id)
	context = request.GET.get('context',None)
	if context=='graph':
		actions = models.Action.objects.filter(paradigm_id__exact=pid).values('type','color')
		alist = list(actions)
		s = simplejson.dumps(alist)
		return HttpResponse(s, content_type="application/json")
	else:
		actions = models.Action.objects.filter(paradigm_id__exact=pid)
		s = serializers.serialize("json", actions)
		return HttpResponse(s, content_type="application/json")

def events_list(request,protocol_id):
	pid = int(protocol_id)
	context = request.GET.get('context',None)
	if context=='graph':
		events = models.Event.objects.filter(protocol_id__exact=pid).values('name','color')
		elist = list(events)
		s = simplejson.dumps(elist)
		return HttpResponse(s, content_type="application/json")
	else:
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