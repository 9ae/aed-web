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

# my django models
from edit.models import Protocol, Paradigm
from models import Experiment

# my modules
from helpers import Medea, poke_cache, cereal
from writers import MarkHappening, NewHappening
import libarian
import boss

def index(request):
	context = {'paradigm_name':'Mickey'}
	return render(request,'index.html',context)

def load_experiment(request):
	m = Medea()
	protocol_id=None
	try:
		protocol_id = int(request.GET['protocol'])
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

def get_experiment(request,eid='bad'):
	m = Medea()
	exp_id=None	
	try:
		exp_id = int(eid)
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

def stop_experiment(request):
	m = Medea()
	experiment_id=None
	try:
		experiment_id = int(request.GET['experiment'])
	except ValueError:
		m.addError('unable to parse protocol id')
	if m.noErrors():
		happs_str = libarian.get_happenings(experiment_id)
		if happs_str=='':
			happs_serial = '[]'
		else:
			happs_serial = json_happenings(happs_str)
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
		hap_str = libarian.get_happening_by_id(hap_id)
		serialized_list.append(hap_str)
		#send to flag as written
		MarkHappening(hap_id).start()
	# update db and cache with empty string
	libarian.clear_happenings(exp_id)
	list_str = ','.join(serialized_list)
	list_str = '['+list_str+']'
	return list_str

def happenings(request):
	experiment_id = int(request.GET['experiment'])
	happs_str = libarian.get_happenings(experiment_id)
	if happs_str=='':
		response_str = '{"happenings":[]}'
		return HttpResponse(response_str, content_type="application/json")
	else:
		#get list of happenings
		list_str = json_happenings(happs_str,experiment_id)
		response_str = '{"happenings":'+list_str+'}'
		return HttpResponse(response_str, content_type="application/json")

def mark(request):
	experiment_id = int(request.GET['experiment'])
	exp_time = libarian.time_since_exp(experiment_id)
	NewHappening('MRK','Mark Point',exp_time,experiment_id).start()
	return HttpResponse('{"ok":true}', content_type="application/json")