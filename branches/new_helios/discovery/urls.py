from django.conf.urls.defaults import *

urlpatterns = patterns('discovery.views',
    (r'^$', 'index'),
    (r'^search/$', 'search'),
    (r'^item/$', 'item'),
    (r'^feed/atom/$', 'atomFeed'),
    (r'^feed/rss/$', 'rssFeed')
)

