from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^upload/(?P<id>\d+)/$', 'imagecrop.views.upload', name='upload'),
    url(r'^upload/', 'imagecrop.views.upload_noid', name='upload_noid'),
    #url(r'^getsrc/(?P<id>\d+)/(?P<nome_atributo>[\w\d-]+)/', 'publicacao.views.get_imagem_to_crop'),
)
