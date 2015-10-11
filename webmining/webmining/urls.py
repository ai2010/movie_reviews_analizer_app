from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from rest_framework import routers
from webmining.pages.api  import PagesList
#from django.views.generic.simple import direct_to_template
#router = routers.DefaultRouter()

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),
    #url(r'^', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^$','webmining.views.analyzer'),
    url(r'^pg-rank/(?P<pk>\d+)/','webmining.views.pgrank_view', name='pgrank_view'),
    url(r'^pages-list/', PagesList.as_view(), name='pages-list'),
    url(r'^about/','webmining.views.about'),
    (r'^assets/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    
)
