# generic python  imports
import json

# django imports
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

# my django models
from edit.models import Protocol, Paradigm
from models import Experiment

# my modules
from helpers import Medea, poke_cache
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
			response_str = serializers.serialize("json", [db_exp])
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
		response_str = serializers.serialize("json",[experiment])
	else:
		response_str = m.serialize()
	return HttpResponse(response_str, content_type="application/json")

def stop_experiment(request):
	experiment =  libarian.get_experiment_current()
	libarian.set_experiment_terminate() 
	response_str = serializers.serialize("json",[experiment])
	return HttpResponse(response_str, content_type="application/json")