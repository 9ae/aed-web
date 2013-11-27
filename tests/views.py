# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.core.cache import cache
from datetime import datetime
import time
import json
import mytest

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
	return HttpResponse(json.dumps(clocky),mimetype='application/json')

def run_triad(request):
	mytest.TriadFinder().run()
	return HttpResponse({'thread':'started'}, content_type="application/json")

def check_triad(request):
	result = {'done':False}
	if mytest.checkTriadComplete():
		result['done'] = True
	
	return HttpResponse(json.dumps(result), content_type="application/json")

def test_cache(request):
	results = {'cache_hit':True,'greeting':''}
	greeting = cache.get('greeting')
	if greeting==None:
		results['cache_hit'] = False
		greeting = 'hello world'
		cache.set('greeting',greeting,60)
	results['greeting'] = greeting
	return HttpResponse(json.dumps(results), content_type="application/json")