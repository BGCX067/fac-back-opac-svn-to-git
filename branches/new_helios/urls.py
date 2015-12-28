from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    # Example:
    (r'^helios/', include('discovery.urls')),
    (r'^helios/media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.BASE_DIR + '/media/'}),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)
