import os
from PIL import  Image
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.core.exceptions import ImproperlyConfigured
from django.forms.util import flatatt
import json


"""
Widget providing Image-crop for cropping image.
"""
class ImageCropWidget(forms.FileInput):
    dimensions = None
    
    class Media:
        try:
            js = (
                settings.STATIC_URL + 'imagecrop/js/jquery.min.js',
                #settings.STATIC_URL + 'imagecrop/js/jquery.Jcrop.min.js',
                settings.STATIC_URL + 'imagecrop/js/jquery.knob.js',
                settings.STATIC_URL + 'imagecrop/js/imgareaselect/jquery.imgareaselect.pack.js',
                settings.STATIC_URL + 'imagecrop/js/admin_crop.js',
            )
            css = {
                'all':(#settings.STATIC_URL + 'imagecrop/css/jquery.Jcrop.css',
                       settings.STATIC_URL + 'imagecrop/css/admin_crop.css',
                       settings.STATIC_URL + 'imagecrop/css/imgareaselect/imgareaselect-animated.css',),
            }
            
        except AttributeError:
            raise ImproperlyConfigured("\"imagecrop\" requires a valid STATC_URL setting. ")
        
    def __init__(self, dimensions, *args, **kwargs):
        self.dimensions = dimensions
        super(ImageCropWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs={}):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        attr_name = final_attrs['name']
        
        model_id = 0
        instance = None
        original_size = ""
        original_src = ""
        original_size_str = ""
        dimensions_str = ""
        if self.form_instance.instance.id > 0:
            model_id = self.form_instance.instance.id
            instance = self.form_instance.instance
            img_attr_obj = getattr(instance, attr_name)
            
            upload_to = img_attr_obj.field.upload_to
            
            last_original_path = img_attr_obj.path
            last_slash = last_original_path.rfind("/")
            
            if last_slash == -1:
                last_slash = last_original_path.rfind("\\")
            
            last_original_name = last_original_path[last_slash+1:]
            last_original_name = last_original_name.replace(attr_name, 
                                                            attr_name+"_original")
            
            original_src = os.path.join(upload_to, last_original_name)
            original_path = os.path.join(settings.MEDIA_ROOT ,upload_to, last_original_name)
            original_size = Image.open(original_path).size
            
            original_size_str = "%i,%i"%(original_size[0], original_size[1])
            dimensions_str = "%i,%i"%(self.dimensions[0], self.dimensions[1])
        
        model_name = self.form_instance.Meta.model.__name__
        model_package = self.form_instance.Meta.model.__dict__['__module__']
        
        return mark_safe(render_to_string('imagecrop/widget.html', {
            'final_attrs': flatatt(final_attrs),
            'value': conditional_escape(force_unicode(value)),
            'id': final_attrs['id'],
            'field_name': attr_name,
            'model_name': model_name,
            'model_package': model_package,
            'model_id' : model_id,
            'instance' : instance,
            'dimensions': dimensions_str,
            'original_src' : original_src,
            'original_size' : original_size_str,
            #'config': json_encode(self.config)
        }))
