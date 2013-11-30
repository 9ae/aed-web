from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^experiment/start$', views.load_experiment),
	url(r'^experiment/stop$', views.stop_experiment),
	url(r'^experiment/(?P<eid>\d+)$', views.get_experiment),
	url(r'^happenings$', views.happenings),
)
