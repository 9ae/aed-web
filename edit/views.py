# Create your views here.

from decimal import Decimal
import json

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.utils import simplejson
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum

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
	
@csrf_exempt
def new_interval(request,protocol_id):
	m = Medea()
	pid = int(protocol_id)
	protocol = None
	try:
		protocol = models.Protocol.objects.get(id=pid)
	except ObjectDoesNotExist:
		m.addError('Protocol ID not found')
		return HttpResponse(m.serialize(),content_type="application/json")
	itype = request.POST.get('type',None)
	if itype==None:
		m.addError('Interval type must be specified')
		return HttpResponse(m.serialize(),content_type="application/json")
	iname = request.POST.get('name',itype);
	iduration = request.POST.get('duration','0.0')
	iduration = Decimal(iduration)
	icolor = request.POST.get('color','000000')
	if len(icolor)==7:
		icolor = icolor[1:]
	iprops = request.POST.get('props',None)
	iprops = json.loads(iprops)
	
	iorder = models.Interval.objects.filter(protocol=protocol).count() + 1
	
	interval = models.Interval(protocol=protocol,order=iorder,type=itype,duration=iduration,name=iname,color=icolor)
	interval.save()
	
	names_id_map = {}	
	for i in range(0,len(iprops)):
		p = iprops[i]
		prop = models.AIEProperty(prop_type=p['type'],prop_name=p['name'])
		prop.set(p['value'])
		prop.save()
		interval.props.add(prop)
		names_id_map[prop.prop_name] = prop.pk
	
	m.addContent('interval_id', interval.pk)
	m.addContent('prop_ids',names_id_map)
	return HttpResponse(m.serialize(),content_type="application/json")

@csrf_exempt
def edit_interval(request,interval_id):
	m = Medea()
	iid = int(interval_id)
	interval = None
	try:
		interval = models.Interval.objects.get(id=iid)
	except ObjectDoesNotExist:
		m.addError('Interval ID not found')
		return HttpResponse(m.serialize(),content_type="application/json")
	
	iname = request.POST.get('name',None)
	if iname!=None:
		interval.name = iname
	
	iduration = request.POST.get('duration',None)
	if iduration!=None:
		interval.duration = Decimal(iduration)
	
	icolor = request.POST.get('color',None)
	if icolor!=None:
		if len(icolor)==7:
			icolor = icolor[1:]
		interval.color = icolor
	
	interval.save()
	
	iprops = request.POST.get('props',[])
	iprops = json.loads(iprops)
		
	for i in range(0,len(iprops)):
		p = iprops[i]
		prop = models.AIEProperty.objects.get(id=p['id'])
		prop.set(p['value'])
		prop.save()
	
	# calculate offsets
	pps = request.POST.get('pps',1.0)
	pps = Decimal(pps)
	sumresult = models.Interval.objects.filter(protocol_id__exact=interval.protocol.pk, order__lte=interval.order).aggregate(Sum('duration'))
	sofar = sumresult['duration__sum']
	sofar = sofar*pps
	ivals_after = models.Interval.objects.filter(protocol_id__exact=interval.protocol.pk, order__gt=interval.order)
	offsetMap = {}
	for poi in ivals_after:
		offsetMap['rect'+str(poi.pk)] = str(sofar)
		sofar = sofar + (poi.duration*pps)

	m.addContent('graphOffsets',offsetMap)	
	return HttpResponse(m.serialize(),content_type="application/json")

def delete_interval(request,interval_id):
	m = Medea()
	iid = int(interval_id)
	interval = None
	try:
		interval = models.Interval.objects.get(id=iid)
	except ObjectDoesNotExist:
		m.addError('Interval ID not found')
		return HttpResponse(m.serialize(),content_type="application/json")
	
	# TODO: disassocate actions
	
	pps = request.GET.get('pps',1.0)
	pps = Decimal(pps)
	sumresult = models.Interval.objects.filter(protocol_id__exact=interval.protocol.pk, order__lt=interval.order).aggregate(Sum('duration'))
	sofar = sumresult['duration__sum']
	if sofar==None:
		sofar = Decimal('0.0')
	sofar = sofar*pps
	ivals_after = models.Interval.objects.filter(protocol_id__exact=interval.protocol.pk, order__gt=interval.order)
	offsetMap = {}
	for poi in ivals_after:
		offsetMap['rect'+str(poi.pk)] = str(sofar)
		sofar = sofar + (poi.duration*pps)
		poi.order = poi.order - 1
		poi.save()
	m.addContent('graphOffsets',offsetMap)	
	
	interval.delete()
	
	return HttpResponse(m.serialize(),content_type="application/json")

@csrf_exempt
def new_event(request,protocol_id):
	m = Medea()
	pid = int(protocol_id)
	protocol = None
	try:
		protocol = models.Protocol.objects.get(id=pid)
	except ObjectDoesNotExist:
		m.addError('Protocol ID not found')
		return HttpResponse(m.serialize(),content_type="application/json")
	etype = request.POST.get('type',None)
	if etype==None:
		m.addError('Event type must be specified')
		return HttpResponse(m.serialize(),content_type="application/json")
	ename = request.POST.get('name',etype);
	color = request.POST.get('color','000000')
	if len(color)==7:
		color = color[1:]
	props = request.POST.get('props',None)
	props = json.loads(props)
	
	event = models.Event(protocol=protocol,type=etype, name=ename, color=color)
	event.save()
	
	names_id_map = {}	
	for i in range(0,len(props)):
		p = props[i]
		prop = models.AIEProperty(prop_type=p['type'],prop_name=p['name'])
		prop.set(p['value'])
		prop.save()
		event.props.add(prop)
		names_id_map[prop.prop_name] = prop.pk
	
	m.addContent('event_id', event.pk)
	m.addContent('prop_ids',names_id_map)
	return HttpResponse(m.serialize(),content_type="application/json")

@csrf_exempt
def edit_event(request,event_id):
	m = Medea()
	eid = int(event_id)
	event = None
	try:
		event = models.Event.objects.get(id=eid)
	except ObjectDoesNotExist:
		m.addError('Event ID not found')
		return HttpResponse(m.serialize(),content_type="application/json")
	
	name = request.POST.get('name',None)
	if name!=None:
		event.name = name
	
	color = request.POST.get('color',None)
	if color!=None:
		if len(color)==7:
			color = color[1:]
		event.color = color
	
	event.save()
	
	props = request.POST.get('props',[])
	props = json.loads(props)
		
	for i in range(0,len(props)):
		p = props[i]
		prop = models.AIEProperty.objects.get(id=p['id'])
		prop.set(p['value'])
		prop.save()
	
	return HttpResponse(m.serialize(),content_type="application/json")