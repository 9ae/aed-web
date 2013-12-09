from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^protocol/(?P<protocol>\d+)/experiment/start$', views.load_experiment),
	url(r'^experiment/(?P<experiment>\d+)/stop$', views.stop_experiment),
	url(r'^experiment/(?P<experiment>\d+)$', views.get_experiment),
	url(r'^experiment/(?P<experiment>\d+)/happenings$', views.happenings),
	url(r'^experiment/(?P<experiment>\d+)/mark$',views.mark),
	url(r'^experiment/(?P<experiment>\d+)/emulate$', views.emulate),
	url(r'^experiment/(?P<experiment>\d+)/simulate$', views.simulate),
)
