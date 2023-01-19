from django.core.validators import ValidationError
import os

def allow_only_image(value):
    ext = os.path.splitext(value.name)[1]
    valid_extension = ['.png', '.jpg', '.jpeg']
    if not ext.lower() in valid_extension:
        raise ValidationError('Unsupported File Extension. Allowed Extensions:' + str(valid_extension))