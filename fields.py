from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.db import models
from django import forms

from imagecrop.widgets import ImageCropWidget


class ImageCropField(models.ImageField):
    def __init__(self, dimensions, *args, **kwargs):
        self.dimensions = dimensions
        super(ImageCropField, self).__init__(*args, **kwargs)
        
        """
        crop_defaults = getattr(settings, 'CROP_DEFAULTS', None)
        
        if self.class_name not in crop_defaults:
            raise ImproperlyConfigured("The model \"%s\" that you set on "
                "ImageCropField constructor is not specified on "
                "\"CROP_DEFAULTS\" at settings.py.\nMake sure you provided "
                "exactly the same path in both \"FormField constructor\", and "
                "\"CROP_DEFAULTS\"."%self.class_name)
        """
    
    def formfield(self, **kwargs):
        # This method is being overridden and will instantiate the FormField 
        # class based on the defaults dict below "defaults". The first key 
        # form_class" gets the FormField class Name while all the other keys are
        # the "FormField" constructor parameters
        defaults = {
            'form_class': ImageCropFormField,
            'dimensions': self.dimensions,
            #'parameter1':'value',
            #'parameter2':'value'
        }
        defaults.update(kwargs)
        return super(ImageCropField, self).formfield(**defaults)


# This class represents the the field object on the form. It recieves as parameter
# the custom widget that will render the HTML for the field
class ImageCropFormField(forms.fields.ImageField):
    
    def __init__(self, dimensions, *args, **kwargs):
        kwargs.update({'widget': ImageCropWidget(dimensions)})
        super(ImageCropFormField, self).__init__(*args, **kwargs)
    

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^imagecrop\.fields\.ImageCropField"])
except:
    pass
