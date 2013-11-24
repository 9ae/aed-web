# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from datetime import datetime
import time
from django.utils import simplejson

def index(request):
	return HttpResponse("Hello")

def toki(request):
	'''
	import sys
	sys.path.append('/media/Rastaban/Workspaces/python/LabPy')
	import sysaid
	'''
	pluto = datetime.now()
	context = {'render_time':datetime.now()}
	return render(request,'toki.html',context)

def ring(request):
	got_request_time = datetime.now()
	clocky = {'got_time': got_request_time.time().isoformat()}
	#do some stuff
	for i in range(0,1999):
		print i
	sent_response_time = datetime.now()
	clocky['sent_time'] = sent_response_time.time().isoformat()
	return HttpResponse(simplejson.dumps(clocky),mimetype='application/json')
