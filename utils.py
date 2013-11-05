# -*- coding: utf8 -*-

import os
import copy
import time as time_module
from cStringIO import StringIO
import psycopg2
from datetime import datetime
from urlparse import urlparse
from PIL import Image, ImageOps, ImageChops
import urllib2 as urllib
import json
from bs4 import BeautifulSoup
from datetime import date
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.conf.urls import url

def adjust_img(path, width_ratio, height_ratio, min_width, min_height ):
    img = Image.open(path)
    if img.mode == 'CMYK':
        img = img.convert('RGB')
    width = float( img.size[0] )
    height = float( img.size[1] )
    
    calc_width = ( width / height ) * height_ratio
    calc_height = ( height / width ) * width_ratio
    
    if calc_width < min_width:
        new_height = ( height / width ) * min_width
        dim = min_width, int(new_height)
        out = ImageOps.fit(img, dim, Image.NEAREST, 0, (0.0,0.0))
        
    elif calc_height < min_height:
        new_width = ( width / height ) * min_height
        dim = int(new_width), min_height
        out = ImageOps.fit(img, dim, Image.NEAREST, 0, (0.0,0.0))
    
    else:
        if width < height  or width == height:
            new_height = ( height / width ) * min_width
            dim = min_width, int(new_height)
            out = ImageOps.fit(img, dim, Image.ANTIALIAS, 0, (0.0,0.0))
        elif width > height:
            new_width = ( width / height ) * min_height
            dim = int(new_width), min_height
            out = ImageOps.fit(img, dim, Image.ANTIALIAS, 0, (0.0,0.0))
            
    return out

def get_img_size(path):
    img = Image.open(path)
    width = img.size[0]
    height = img.size[1]
    
    ratio_width = ( width / height ) * 480
    ratio_heith = ( height / width ) * 640

def getBox(img, largura, altura):
    corte_left = ( img.size[0] / 2 ) - ( largura / 2 )
    corte_up = ( img.size[1] / 2 ) - ( altura / 2 )
    
    corte_right = corte_left + largura
    corte_down = corte_up + altura
    return (corte_left, corte_up, corte_right, corte_down)


def remove_values_from_list(the_list, val):
    for ii in range(the_list.count(val)):
        the_list.remove(val)

def get_temp_name(campo):
    time = int(datetime.now().microsecond)
    upload_to = campo.field.upload_to
    file_name = campo.name[campo.name.rfind("/")+1:]
    extensao = file_name[file_name.rfind("."):]
    
    return "%stemp_%s%s" % (upload_to, time, extensao)
    
    
def get_ip_from_request(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip == None:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def add_categoria_view(request, categoria):
    from core.models import CategoriaVisualizacoes
    ip = get_ip_from_request(request)
    
    visualizacoes = CategoriaVisualizacoes.objects.filter(
        ip = ip,
        categoria = categoria,
    )
    
    if len(visualizacoes) > 0:
        visualizacao = visualizacoes[0]
        visualizacao.quantidade += 1
        visualizacao.save()
    else:
        visualizacao = CategoriaVisualizacoes()
        visualizacao.ip = ip
        visualizacao.categoria = categoria
        visualizacao.quantidade = 1
        visualizacao.save()
    
def add_publicacao_view(request, publicacao):
    from core.models import PublicacaoVisualizacoes
    ip = get_ip_from_request(request)

    visualizacoes = PublicacaoVisualizacoes.objects.filter(
        ip = ip,
        publicacao = publicacao,
    )
    
    if len(visualizacoes) > 0:
        visualizacao = visualizacoes[0]
        visualizacao.quantidade += 1
        visualizacao.save()
    else:
        visualizacao = PublicacaoVisualizacoes()
        visualizacao.ip = ip
        visualizacao.publicacao = publicacao
        visualizacao.quantidade = 1
        visualizacao.save()

def add_autor_view(request, autor):
    from core.models import AutorVisualizacao
    ip = get_ip_from_request(request)

    visualizacoes = AutorVisualizacao.objects.filter(
        ip = ip,
        autor = autor,
    )
    
    if len(visualizacoes) > 0:
        visualizacao = visualizacoes[0]
        visualizacao.quantidade += 1
        visualizacao.save()
    else:
        visualizacao = AutorVisualizacao()
        visualizacao.ip = ip
        visualizacao.autor = autor
        visualizacao.quantidade = 1
        visualizacao.save()
    
def add_review_view(request, review):
    from core.models import ReviewVisualizacao
    ip = get_ip_from_request(request)
    
    visualizacoes = ReviewVisualizacao.objects.filter(
        ip = ip,
        review = review,
    )
    
    if len(visualizacoes) > 0:
        visualizacao = visualizacoes[0]
        visualizacao.quantidade += 1
        visualizacao.save()
    else:
        visualizacao = ReviewVisualizacao()
        visualizacao.ip = ip
        visualizacao.review = review
        visualizacao.quantidade = 1
        visualizacao.save()

def execute_query(sql):
    try:
        host = settings.DATABASES['default']['HOST']
        user = settings.DATABASES['default']['USER']
        password = settings.DATABASES['default']['PASSWORD']
        db_name = settings.DATABASES['default']['NAME']
        
        conn_string = "host='%s' dbname='%s' user='%s' password='%s'" %(host, db_name, user, password)
        connection = psycopg2.connect(conn_string)
        
        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        connection.close()
    except Exception, e:
        rows = None
    return rows

def get_pk_list(list):
    pk_list = []
    for item in list:
        pk_list.append(item.id)
    return pk_list

def get_paginator(num_page, object_list, pagination_max, adjacent_pages):
    num_page = int(num_page)
    paginator = Paginator(object_list, pagination_max)
                
    try:
        page = paginator.page(num_page)
    except:
        page = paginator.page(paginator.num_pages)
        
    page_numbers = [n for n in \
        range(num_page - adjacent_pages, num_page + adjacent_pages + 1) \
        if n > 0 and n <= paginator.num_pages]
    
    pagination_data = {
        #'hits': context['hits'], #total de Instancias
        'results_per_page': pagination_max,
        'page_num': num_page, #era "page" a chave
        'pages': paginator.num_pages,
        'page_numbers': page_numbers,
        'next': page.next_page_number() if page.has_next() else None,
        'previous': page.previous_page_number() if page.has_previous() else None,
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
        'show_first': 1 not in page_numbers,
        'show_last': paginator.num_pages not in page_numbers,
        'page' : page,
    }
    
    return page.object_list, pagination_data

def get_publicacoes_mais_vistas(intervalo):
    from core.models import Publicacao
    sql_mais_vistas = """
        SELECT publicacao_id, COUNT(  `publicacao_id` ) AS  `count` 
        FROM  `core_publicacaovisualizacoes`
        WHERE date_format(data, '%%Y-%%m-%%d') BETWEEN DATE_SUB(CURRENT_DATE, INTERVAL %s DAY) AND curdate()
        GROUP BY  `publicacao_id` 
        ORDER BY COUNT(  `publicacao_id` ) DESC 
        LIMIT 5;
    """ %( intervalo )
    
    rows = execute_query(sql_mais_vistas);
    mais_vistas = []
    
    for row in rows:
        mais_vistas.append(Publicacao.objects.get( pk=row[0]) )
        
    return mais_vistas

def get_reviews_mais_vistas(intervalo):
    from core.models import Review
    sql_mais_vistas = """
        SELECT review_id, COUNT(  `review_id` ) AS  `count` 
        FROM  `core_reviewvisualizacoes`
        WHERE date_format(data, '%%Y-%%m-%%d') BETWEEN DATE_SUB(CURRENT_DATE, INTERVAL %s DAY) AND curdate()
        GROUP BY  `review_id` 
        ORDER BY COUNT(  `review_id` ) DESC 
        LIMIT 5;
    """ %( intervalo )
    
    rows = execute_query(sql_mais_vistas);
    mais_vistas = []
    
    for row in rows:
        mais_vistas.append(Review.objects.get( pk=row[0]) )
        
    return mais_vistas

def get_anteriores(item_anterior, lista, historico):
    if not historico:
        historico = []
        anteriores = item_anterior.get_anteriores()
        
    if len(anteriores) > 0:
        for item in anteriores:
            if item.mostrar_antes not in historico:
                if item.mostrar_antes.status == 'pb':
                    historico.append(item.mostrar_antes)
                    get_anteriores(item.mostrar_antes, lista, historico)
                    lista.append(item.mostrar_antes)
    
    return lista


class Previsao:
    dia = None
    temp = None
    maxima = None
    minima = None
    iuv = None

class CPTEC:
    url = None
    cidade = None
    uf = None
    atualizacao = None
    previsoes = None
    
    def __init__(self, url):
        self.url = url
        try:
            content = urllib.urlopen(url)
            xml = content.read()
            xml_obj = BeautifulSoup(xml)
            
            self.cidade = xml_obj.cidade.nome.string
            self.uf = xml_obj.cidade.uf.string
            self.atualizacao = xml_obj.cidade.atualizacao.string
            
            previsoes = xml_obj.find_all('previsao')
            self.previsoes = []
            for previsao in previsoes:
                obj_previsao = Previsao()
                dia = previsao.dia.string
                amd = dia.split('-')
                
                obj_previsao.dia = date(int(amd[0]), int(amd[1]), int(amd[2]))
                obj_previsao.tempo = previsao.tempo.string
                obj_previsao.maxima = previsao.maxima.string
                obj_previsao.minima = previsao.minima.string
                obj_previsao.iuv = previsao.iuv.string
                
                self.previsoes.append(obj_previsao)
        except Exception, e:
            return None

def handle_image_from_xhr_upload(request, instance, attr_name):
    inicio = time_module.time()
    if attr_name in request.FILES:
        image_file = request.FILES[attr_name]
        img_name = image_file.name
    
    elif 'url' in request.POST: # If image comes from url
        url = request.POST['url']
        url = url.replace(" ", "%20")
        imgcontent = urllib.urlopen(url) # open the image contents
        image_file = StringIO(imgcontent.read()) # creates an in memory file object
        
        parsed_url = urlparse(url)
        img_name = parsed_url.path # gets the file name on url
    
    extension = img_name[img_name.rfind("."):] # gets the image extension
    
    # gets the ImageCrop attribute from the model
    image_crop_attr_obj = getattr(instance, attr_name) 
    
    upload_to = image_crop_attr_obj.field.upload_to
    time = int(datetime.now().microsecond)# current time to add on the file name
    
    # Open the uploaded (or downloaded in case it's from url) image
    image_file = Image.open(image_file)
    img_attr_obj = getattr(instance, attr_name)
    
    try:
        os.remove(img_attr_obj.path)
    except:
        pass
    
    try:
        last_original_path = img_attr_obj.path
        last_slash = last_original_path.rfind("/")
        
        if last_slash == -1:
            last_slash = last_original_path.rfind("\\")
        
        last_original_name = last_original_path[last_slash+1:]
        last_original_name = last_original_name.replace(attr_name, 
                                                        attr_name+"_original")
        
        os.remove(os.path.join(settings.MEDIA_ROOT, upload_to, last_original_name))
    except:
        pass
        
    ready_image_file = None
    ready_image_file = StringIO()
    image_file.save(ready_image_file , 'PNG', optimize = True)
    ready_image_file.seek(0)
    
    # Set the uploaded image to the file attribute of the imagefield
    img_attr_obj.file = ready_image_file
    
    # Seta o novo nome da imagem upada para o campo atual da iteracao (upload_to/nome.jpg)
    image_original_name = "%s%s_original_%s_%s%s" % (upload_to, attr_name, instance.id, time, extension)
    
    img_attr_obj.name = "%s%s_%s_%s%s" % (upload_to, attr_name, instance.id, time, extension)
    
    # Abre e salva a imagem atual no sistema de arquivos
    image_obj = Image.open( img_attr_obj )
    
    #image_obj.
    image_obj.save( img_attr_obj.path )
    
    # Dimensoes para usar como parametro na funcao adjust_img()
    dim = img_attr_obj.field.dimensions
    
    # Cria uma imagem cropavel ajustada para o tamanho especificado para o campo atual
    adjusted_image = adjust_img(img_attr_obj.path, dim[0], dim[1], dim[0], dim[1])
    adjusted_image.save( os.path.join(settings.MEDIA_ROOT,image_original_name))
    original_img_dim = adjusted_image.size
    
    box = getBox(adjusted_image, dim[0], dim[1])
    
    cropped_img = adjusted_image.crop(box)
    
    # Salva a imagem cropada no lugar da anterior (a imagem upada não tratada)
    cropped_img.save( img_attr_obj.path )
    cropped_img_dim = cropped_img.size
    
    instance.save()
    
    data = serializers.serialize("json", [instance])
    
    json_as_python = json.loads(data)
    
    original_dict_key = {
        attr_name+'_original': {
            'src':os.path.join("/media/", image_original_name),
            'dimensions':"%i,%i"%(original_img_dim[0], original_img_dim[1]),
        }
    }
    
    cropped_imgage = {
        attr_name+'_cropped': {
            'src': os.path.join("/media/", img_attr_obj.name),
            'dimensions':"%i,%i"%(cropped_img_dim[0], cropped_img_dim[1]),
        }
    }
    
    json_as_python[0].update(original_dict_key)
    json_as_python[0].update(cropped_imgage)
    
    data = json.dumps(json_as_python)
    return data

def crop_attribute_image(instance, box, atributo):

    str_temp = atributo[atributo.rfind("_")+1:]
    
    time = int(datetime.now().microsecond)
    obj_campo = getattr(instance, atributo)
    upload_to = obj_campo.field.upload_to
    
    old_path = obj_campo.path # guarda o path da imagem anterior
    old_name_ext = obj_campo.name[obj_campo.name.rfind("/")+1:] # guarda o nome da imagem anterior com o time
    old_name = old_name_ext[:old_name_ext.rfind("_")+1] # guarda o nome da imagem anterior sem o time
    extensao = old_name_ext[old_name_ext.rfind("."):] # guarda a extensao
    
        
    if str_temp != "temp":
        obj_attr = getattr(instance, atributo+"_cropbox")
        str_box = "%s,%s,%s,%s" % (box[0], box[1], box[2], box[3])
        setattr(instance, atributo+"_cropbox", str_box )
    
    img = Image.open( instance.imagem_temp_crop.path )
    croped = img.crop(box)
    
    obj_campo.name = "%s%s%s%s" % (upload_to, old_name, time, extensao) # atribui o nome da nova imagem ao campo
    croped.save(obj_campo.path)
        
    try:
        os.remove(old_path)
    except:
        pass
    
    # Remove a imagem temporaria
    try:
        os.remove(instance.imagem_temp_crop.path)
        instance.imagem_temp_crop = None
    except:
        pass
        
    instance.save()
    
    data = {}
    
    crop_settings_dict_key = instance._meta.module_name
    iter_crop_settings = iter(settings.CROP_SETTINGS[crop_settings_dict_key])
    
    for (counter, campo) in enumerate(iter_crop_settings):
        if campo != 'imagem_original':
            if str_temp == 'temp':
                data[campo+"_"+str_temp] = getattr(instance, campo+"_"+str_temp).name
            else:
                data[campo] = getattr(instance, campo).name
    
    data['atributo']  = atributo
    data['temp'] = str_temp == "temp"
    
    json_data = json.dumps(data)
    return json_data

def get_cropable_img(instance, nome_atributo, crop_settings_dict_key):
    
    try:
        os.remove(instance.imagem_temp_crop.path)
    except:
        pass
    
    time = int(datetime.now().microsecond)
    campo = getattr(instance, nome_atributo)
    upload_to = campo.field.upload_to
    file_name = campo.name[campo.name.rfind("/")+1:]
    extensao = file_name[file_name.rfind("."):]

    str_temp = nome_atributo[nome_atributo.rfind("_"):]
    
    if str_temp != "_temp":
        key = nome_atributo
        str_temp = ""
    else:
        key = nome_atributo.replace(str_temp,"")
    
    prefix = settings.CROP_PREFIX[key]

    temp_name = "%stemp_%s%s" % (upload_to, time, extensao)
    instance.imagem_temp_crop.name = temp_name
    
    temp_img = getattr(instance,"get_tempfile_"+prefix+str_temp)()
    instance.save()
    temp_img.save(instance.imagem_temp_crop.path)
    src = "%s%s" % (settings.MEDIA_URL, temp_name)
    
    return src
            
            

def previsao_tempo():
    url = "http://servicos.cptec.inpe.br/XML/cidade/3920/previsao.xml"
    cptec = CPTEC(url)
    return cptec

def make_thumb_fixed_dimension(f_in, size):

    image = f_in
    image.thumbnail(size, Image.ANTIALIAS)
    image_size = image.size
    
    thumb = ImageOps.fit(image, size, Image.ANTIALIAS, (0.5, 0.5))

    return thumb

