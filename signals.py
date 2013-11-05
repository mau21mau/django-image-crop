import os
from django.conf import settings
from imagecrop.fields import ImageCropField

def delete_files_from_field(sender, **kwargs):
    instance = kwargs.get('instance')
    
    attr_list = dir(instance)
    for attr in attr_list:
        
        try:
            img_attr_obj = getattr(instance, attr)
            if type(img_attr_obj.field) == ImageCropField:
                
                attr_name = img_attr_obj.field.name
                last_original_path = img_attr_obj.path
                last_slash = last_original_path.rfind("/")
                
                if last_slash == -1:
                    last_slash = last_original_path.rfind("\\")
                
                original_name = last_original_path[last_slash+1:]
                original_name = original_name.replace(attr_name, 
                                                      attr_name+"_original")
                
                upload_to = img_attr_obj.field.upload_to
                os.remove(os.path.join(settings.MEDIA_ROOT, upload_to,
                                       original_name))
                
                os.remove(img_attr_obj.path)
                
        except:
            pass
    