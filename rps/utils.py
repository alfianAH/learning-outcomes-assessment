import os
import uuid
from django.conf import settings


def rps_upload_handler(instance, filename):
    _, extension = os.path.splitext(filename)
    new_filename = '{}{}'.format(uuid.uuid1(), extension)
    
    file_path = os.path.join(settings.MEDIA_ROOT, 'mk-semester', 'rps', new_filename)
    return file_path 
