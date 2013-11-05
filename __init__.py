import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models.loading import get_model
from django.db.models.signals import pre_delete
from imagecrop.signals import delete_files_from_field

if 'imagecrop' in settings.INSTALLED_APPS:
    # Confirm CROP_DEFAULTS setting has been specified.
    try:
        settings.CROP_DEFAULTS
        # iterates over the models using the ImageCropField
        for model_path in settings.CROP_DEFAULTS:
            model_name = None
            model_package = None
        
            path_fragments = model_path.split(".")
            if len(path_fragments) > 1:
                dot_index = model_path.rfind(".")
                model_name = model_path[dot_index+1:]
                model_package = model_path[:dot_index]
                app_label = model_package.split(".")[0]
            
            model = get_model(app_label, model_name)
            
            if model:
                pre_delete.connect(delete_files_from_field, model)
            else:
                raise ImportError("could no import model \"%s\". \n Check at "
                    "your CROP_DEFAULTS settings if the model path is "
                    "correctlly specified"%model_path)
    
    
    except AttributeError:
        
        raise ImproperlyConfigured("django-image-crop requires "
            "CROP_DEFAULTS setting. This setting specifies a dictionary "
            "containing the models that are using  ImageCropField and the list"
            " of required attributes with it's default values. Make sure you "
            "have write permissions for the  path, i.e.: \n "
            "CROP_DEFAULTS = {\n"
            "    'yourapp.models.YourModel':{\n"
            "        'name':'Insert a name'\n"
            "        'email':'Insert an email'\n"
            "     }\n"
            "}")