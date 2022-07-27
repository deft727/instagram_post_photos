import graphene
from django.core.exceptions import ObjectDoesNotExist

from server.utils import MutationPayload
from accounts.models import User
from accounts.instagram_gallery.models import InstagramGallery

from .services import get_token_and_user_id, parse_response_code
from .access_token_typyng import AccessTokenResult
from .save_post_photo import save_instagram_photo_to_model


class InstagramGalleryMutation(graphene.Mutation, MutationPayload):
    class Arguments:
        code = graphene.String(required=True)

    def mutate(self, info, code):
        errors = list()
        user = info.context.user
        code = parse_response_code(code)
        profile_data = get_token_and_user_id(code)

        try:
            gallery = InstagramGallery.objects.get(user=user)

        except ObjectDoesNotExist:
            gallery = InstagramGallery()
            gallery.user = user
            gallery.save()

        _create_or_update_token(profile_data, user)
        save_instagram_photo_to_model(gallery)
        return InstagramGalleryMutation(errors=errors)


def _create_or_update_token(data: AccessTokenResult, user: User) -> None:
    gallery = InstagramGallery.objects.get(user=user)
    gallery.access_token = data.access_token
    gallery.expires_at = data.expires_at
    gallery.social_id = data.user_id
    gallery.save()
