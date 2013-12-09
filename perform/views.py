# generic python  imports
import json

# django imports
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

# my django models
from edit.models import Protocol, Paradigm, Action
from models import Experiment, EmulateAction, SimEvent

# my modules
from helpers import Medea, poke_cache, cereal
from writers import MarkHappening, NewHappening
import libarian
import boss

def index(request):
	context = {'paradigm_name':'Mickey'}
	return render(request,'index.html',context)

def load_experiment(request,protocol):
	m = Medea()
	protocol_id=None
	try:
		protocol_id = int(protocol)
	except ValueError:
		m.addError('unable to parse protocol id')
	if protocol_id!=None:
		try:
			protocol = Protocol.objects.get(id=protocol_id)
		except ObjectDoesNotExist:
			m.addError('protocol not found')
	if m.noErrors():
		db_exp = boss.setup_experiement(protocol)
		if db_exp!=None:
			response_str = cereal(db_exp)
		else:
			m.addError('failed to import '+protocol.paradigm.name)
			response_str = m.serialize()
	else:
		response_str = m.serialize()
	return HttpResponse(response_str, content_type="application/json")

def get_experiment(request,experiment):
	m = Medea()
	exp_id=None	
	try:
		exp_id = int(experiment)
	except ValueError:
		m.addError('unable to parse id')
	def find_experiment():
		experiment = None
		if exp_id!=None:
			try:
				experiment = Experiment.objects.get(id=exp_id)
			except ObjectDoesNotExist:
				m.addError('experiment not found')
		return experiment
	
	if exp_id!=None:
		cache_key = 'experiment.%d'%exp_id
		experiment = poke_cache(cache_key,find_experiment)
	
	if m.noErrors():
		response_str = cereal(experiment)
	else:
		response_str = m.serialize()
	return HttpResponse(response_str, content_type="application/json")

def stop_experiment(request,experiment):
	m = Medea()
	experiment_id=None
	try:
		experiment_id = int(experiment)
	except ValueError:
		m.addError('unable to parse protocol id')
	if m.noErrors():
		happs_str = libarian.get_happenings(experiment_id)
		if happs_str=='':
			happs_serial = '[]'
		else:
			happs_serial = json_happenings(happs_str,experiment_id)
		libarian.set_experiment_terminate(experiment_id) 
		response_str = '{"happenings":'+happs_serial+'}'
		return HttpResponse(response_str, content_type="application/json")
	else:
		return HttpResponse(m.serialize(), content_type="application/json")
		

def json_happenings(happs_str,exp_id):
	happs_list = happs_str.split(',') 
	happs_list = map(int,happs_list)
	
	#for each happening get its serialized version
	serialized_list = []
	
	for hap_id in happs_list:
		#get hap clear its cache
		hap_str = libarian.get_happening_by_id(hap_id,exp_id)
		serialized_list.append(hap_str)
		#send to flag as written
		MarkHappening(hap_id).start()
	# update db and cache with empty string
	libarian.clear_happenings(exp_id)
	list_str = ','.join(serialized_list)
	list_str = '['+list_str+']'
	return list_str

def happenings(request,experiment):
	experiment_id = int(experiment)
	happs_str = libarian.get_happenings(experiment_id)
	if happs_str=='':
		response_str = '{"happenings":[]}'
		return HttpResponse(response_str, content_type="application/json")
	else:
		#get list of happenings
		list_str = json_happenings(happs_str,experiment_id)
		response_str = '{"happenings":'+list_str+'}'
		return HttpResponse(response_str, content_type="application/json")

def mark(request,experiment):
	experiment_id = int(experiment)
	exp_time = libarian.time_since_exp(experiment_id)
	NewHappening('MRK','Mark Point',exp_time,experiment_id).start()
	return HttpResponse('{"ok":true}', content_type="application/json")

@csrf_exempt
def emulate(request,experiment):
	experiment_id = int(experiment)
	action_id = int(request.POST['action_id']);
	exp = Experiment.objects.get(id=experiment_id)
	act = Action.objects.get(id=action_id)
	exp_time = libarian.time_since_exp(experiment_id)
	ea = EmulateAction(experiment=exp,time_occurred=exp_time,action=act)
	ea.save()
	return HttpResponse('{"ok":true}', content_type="application/json")

@csrf_exempt
def simulate(request,experiment):
	experiment_id = int(experiment)
	event_id = int(request.POST['event_id']);
	exp = Experiment.objects.get(id=experiment_id)
	exp_time = libarian.time_since_exp(experiment_id)
	se = SimEvent(experiment=exp,time_occurred=exp_time,eventid=event_id)
	se.save()
	return HttpResponse('{"ok":true}', content_type="application/json")