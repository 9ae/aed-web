# Create your views here.

from decimal import Decimal

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.utils import simplejson
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

import models
from decadence import json_encode_decimal
from perform.helpers import cereal, import_mod_file, Medea


# from perform.helpers import cereal

def index(request):
	content = {'default_duration':10.0}
	return render(request,'edit.html',content)

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

@csrf_exempt
def make_protocol(request,paradigm_id):
	pid = int(paradigm_id)
	paradigm = models.Paradigm.objects.get(id=pid)
	
	duration = request.POST.get('duration',10)
	name = request.POST.get('name',paradigm.name)
	duration = Decimal(duration)
	
	paradigm_mod = import_mod_file(paradigm.file_location)
	paradigm_obj = eval('paradigm_mod.'+paradigm.name+'()')
	content = paradigm_obj.json()
	
	protocol = models.Protocol(paradigm=paradigm, name=name, trial_duration=duration)
	protocol.save()
	content['protocol_id'] = protocol.pk
	
	s = simplejson.dumps(content)
	return HttpResponse(s,content_type="application/json")

@csrf_exempt
def set_trial_duration(request,protocol_id):
	m = Medea()
	pid = int(protocol_id)
	duration = request.POST.get('duration',None)
	if duration==None:
		m.addError('Trial duration not defined')
		return HttpResponse(m.serialize(),content_type="application/json")
	duration = Decimal(duration)
	try:
		protocol = models.Protocol.objects.get(id=pid)
		protocol.trial_duration = duration
		protocol.save()
		return HttpResponse(m.serialize(),content_type="application/json")
	except ObjectDoesNotExist:
		m.addError('Protocol ID not found')
		return HttpResponse(m.serialize(),content_type="application/json")