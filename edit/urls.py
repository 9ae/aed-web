from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^protocol/(?P<protocol_id>\d+)$', views.get_protocol),
	url(r'^paradigm/(?P<paradigm_id>\d+)/actions$', views.actions_list),
	url(r'^protocol/(?P<protocol_id>\d+)/events$', views.events_list),
	url(r'^protocol/(?P<protocol_id>\d+)/intervals$',views.intervals_list),
	url(r'^protocol/(?P<protocol_id>\d+)/intervals/view',views.intervals_listview),
)
