from django.conf.urls import patterns, url

import contract_views

urlpatterns = patterns('',
                       url(r'(\d+)', contract_views.main_view, name='contract'),
                       )
