from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^toki$', views.toki, name='toki'),
	url(r'^ring$',views.ring,name='ring'),
	url(r'^run_triad$',views.run_triad),
	url(r'^check_triad$',views.check_triad),
)
