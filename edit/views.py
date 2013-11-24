# Create your views here.

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.utils import simplejson

def index(request):
	return HttpResponse("Hello")