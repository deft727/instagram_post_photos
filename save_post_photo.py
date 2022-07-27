import requests
import tempfile

from django.core import files

from accounts.instagram_gallery.models import InstagramGallery, InstagramPostImage


def save_instagram_photo_to_model(gallery: InstagramGallery) -> None:
    image_urls = gallery.get_photos_urls()
    for image_url in image_urls:
        file_name = image_url.split('?')[0].split('/')[-1]
        if not InstagramPostImage.objects.filter(image=f'instagram_images/{file_name}').exists():
            photos = InstagramPostImage()
            photos.gallery = gallery
            response = requests.get(image_url, stream=True)
            if response.status_code != requests.codes.ok:
                continue
            lf = tempfile.NamedTemporaryFile()
            for block in response.iter_content(1024 * 8):
                if not block:
                    break
                lf.write(block)
            photos.image.save(file_name, files.File(lf))
            photos.save()
