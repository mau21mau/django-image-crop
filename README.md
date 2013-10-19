django-image-crop
=================

Django app for cropping images strictly according to a specific dimension ruled by the aspect ratio. If the image is wider than tall, the image to be cropped will have a fixed height crop box according to the height specified on the CropImageField constructor at the model. However if the image is taller than wide, the oposite will happen, where the image to be croped will have  a fixed width cropbox according to the width specified on the constructor.
