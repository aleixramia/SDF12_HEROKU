from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^restaurants/(?P<city>.*)/(?P<category>.*)$', views.restaurants, name='restaurants'),
    url(r'^restaurants/(?P<city>.*)/$', views.restaurants, name='restaurants'),
    #url(r'^restaurants/(?P<category>.*)/$', views.restaurants, name='restaurants'),
    url(r'^restaurants/$', views.restaurants, name='restaurants'),
    url(r'^reservation/$', views.reservation, name='reservation'),
    url(r'^checkout/$', views.checkout, name='checkout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^details/(?P<restaurant_number>.*)/$', views.details, name='details'),
    url(r'^search/$', views.search, name='search'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^review/$', views.review, name='review'),
    url(r'^error/$', views.error, name='error'),
    url(r'^$', views.index, name='index')
]