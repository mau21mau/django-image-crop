# -*- coding: utf8 -*-
import os
import re
from urlparse import urlparse, urlunparse
from datetime import datetime

from django.db.models.loading import get_model
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from imagecrop.utils import handle_image_from_xhr_upload

try:
    from PIL import Image, ImageOps
except ImportError:
    import Image
    import ImageOps

def upload_noid(request):
    model_name = request.POST['model_name']
    model_package = request.POST['package']
    model_path = model_package+"."+model_name
    
    app_label = model_package.split(".")[0]
    
    model = get_model(app_label, model_name)
    
    if 'id' in request.POST:
        id = int(request.POST['id'])
        instance = model.objects.get(pk=id)
    else:
        instance = model()
        default_fields = settings.CROP_DEFAULTS[model_path]['required_fields']
    
        for field, default_value in default_fields.iteritems():
            if hasattr(instance, field):
                setattr(instance, field, default_value)
            else:
                raise AttributeError("The model \"%s\" has no attribute \"%s\". "
                    "Check if it's specified on \"CROP_DEFAULTS\" at settings.py "
                    "or if you typed it correctly."%(model_name, field))
    
    instance.save()
    return upload(request, instance)

#@csrf_exempt
def upload(request, instance):
    attr_name = request.POST["attr_name"]
    json_data = handle_image_from_xhr_upload(request, instance, attr_name)
    response  = HttpResponse(json_data, mimetype = 'plain/text')
    
    return response

def get_imagem_to_crop(request, id, nome_atributo):

    instance = Publicacao.objects.get(pk = id)
    src = get_cropable_img(instance, nome_atributo, 'publicacao')
    return HttpResponse(src)

def jcrop(request, id, corte_left, corte_up, corte_right, corte_down, atributo):
    #time_module.sleep(5)
    corte_left = int(corte_left)
    corte_up = int(corte_up)
    corte_right = int(corte_right)
    corte_down = int(corte_down)
    # Box usado para cropar
    box = (corte_left,corte_up,corte_right,corte_down)
    instance = Publicacao.objects.get(pk = int(id))
    
    json_data = crop_attribute_image(instance, box, atributo)
    
    return HttpResponse(json_data, mimetype = 'plain/text')
