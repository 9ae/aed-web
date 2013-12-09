from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^paradigm/(?P<paradigm_id>\d+)/actions$', views.actions_list),
	url(r'^protocol/(?P<protocol_id>\d+)/events$', views.events_list),
)
