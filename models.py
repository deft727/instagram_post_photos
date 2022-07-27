import requests
import json
from datetime import timedelta
from graphql import GraphQLError

from django.db import models
from django.utils import timezone

from accounts.instagram_gallery.services import get_long_lived_token


class InstagramGallery(models.Model):

    user = models.OneToOneField(
        'accounts.User', on_delete=models.DO_NOTHING, related_name='instagram_gallery')
    access_token = models.CharField(max_length=255, blank=True, null=True, editable=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    social_id = models.BigIntegerField(null=True, blank=True, editable=False)

    @property
    def expires_in(self):
        if self.expires_at:
            return self.expires_at - timezone.now()
        return timedelta(seconds=0)

    @property
    def access_valid(self):
        return self.access_token and self.expires_at and self.expires_at > timezone.now()

    def update_token(self):
        data = get_long_lived_token(self.access_token)
        if data:
            self.access_token = data.get('access_token')
            self.expires_at = data.get('expires_at')
            self.save()

    def get_photos_urls(self):
        if self.access_token and self.expires_in <= timedelta(days=30):
            self.update_token()
        access_token = self.access_token
        r = requests.get(
            f'https://graph.instagram.com/me/media?fields=children,media_url&access_token={access_token}')
        data = json.loads(r.text)
        if data.get('error'):
            raise GraphQLError(f'{data.get("error")}')
        return [i.get('media_url') for i in data.get('data')] if data.get('data') else None


class InstagramPostImage(models.Model):
    gallery = models.ForeignKey(InstagramGallery, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='instagram_photos')
    image = models.ImageField(
        upload_to='instagram_images',
    )
