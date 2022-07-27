import graphene
from graphene_django.types import DjangoObjectType

from django.core.exceptions import ObjectDoesNotExist

from accounts.instagram_gallery.models import InstagramGallery, InstagramPostImage


class InstagramGalleryType(DjangoObjectType):
    class Meta:
        model = InstagramPostImage


class Query:
    instagram_gallery = graphene.List(InstagramGalleryType)

    def resolve_instagram_gallery(self, info):
        user = info.context.user
        try:
            gallery = InstagramGallery.objects.get(user=user)
            return gallery.instagram_photos.all()
        except ObjectDoesNotExist:
            return None
