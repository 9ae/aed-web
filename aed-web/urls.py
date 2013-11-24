from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^tests/',include('tests.urls')),
	url(r'^perform/',include('perform.urls')),
	url(r'^edit/',include('edit.urls')),
	url(r'^admin/', include(admin.site.urls)),
)
