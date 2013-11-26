# Create your views here.

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from edit.models import Protocol, Paradigm
from helpers import Medea
import json
from boss import setupExperiement

from xml.etree import ElementTree as elle
def index(request):
	context = {'paradigm_name':'Mickey'}
	return render(request,'index.html',context)

def load_experiment(request):
	m = Medea()
	protocol_id=None
	try:
		protocol_id = int(request.GET['id'])
	except ValueError:
		m.addError('unable to parse id')
	if protocol_id!=None:
		try:
			protocol = Protocol.objects.get(id=protocol_id)
		except ObjectDoesNotExist:
			m.addError('protocol not found')
	if m.noErrors():
		db_exp = setupExperiement(protocol)
		if db_exp!=None:
			response_str = serializers.serialize("json", [db_exp])
		else:
			m.addError('failed to import '+protocol.paradigm.name)
			response_str = m.serialize()
	else:
		response_str = m.serialize()
	return HttpResponse(response_str, content_type="application/json")
