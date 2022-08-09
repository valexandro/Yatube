from io import BytesIO

import PIL.Image
from django.core.files.uploadedfile import SimpleUploadedFile


def get_test_image(filename='test-image.png',
                   color='white',
                   size=(100, 100)
                   ):
    """Создает и возвращает изображение для тестов."""
    file = BytesIO()
    image = PIL.Image.new('RGBA', size, color)
    image.save(file, 'PNG')
    return SimpleUploadedFile(
        name=filename,
        content=file.getvalue(),
        content_type='image/png'
    )
