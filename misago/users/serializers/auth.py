from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.urls import reverse

from misago.acl import serialize_acl

from .user import UserSerializer


UserModel = get_user_model()

__all__ = [
    'AuthenticatedUserSerializer',
    'AnonymousUserSerializer',
]


class AuthFlags(object):
    def get_is_authenticated(self, obj):
        return bool(obj.is_authenticated)

    def get_is_anonymous(self, obj):
        return bool(obj.is_anonymous)


class AuthenticatedUserSerializer(UserSerializer, AuthFlags):
    email = serializers.SerializerMethodField()
    is_authenticated = serializers.SerializerMethodField()
    is_anonymous = serializers.SerializerMethodField()

    class Meta:
        model = UserModel
        fields = UserSerializer.Meta.fields + [
            'is_hiding_presence',
            'limits_private_thread_invites_to',
            'unread_private_threads',
            'subscribe_to_started_threads',
            'subscribe_to_replied_threads',
            'is_authenticated',
            'is_anonymous',
        ]

    def get_acl(self, obj):
        return serialize_acl(obj)

    def get_email(self, obj):
        return obj.email

    def get_api(self, obj):
        return {
            'avatar': reverse('misago:api:user-avatar', kwargs={'pk': obj.pk}),
            'details': reverse('misago:api:user-details', kwargs={'pk': obj.pk}),
            'options': reverse('misago:api:user-forum-options', kwargs={'pk': obj.pk}),
            'username': reverse('misago:api:user-username', kwargs={'pk': obj.pk}),
            'change_details': reverse('misago:api:user-change-details', kwargs={'pk': obj.pk}),
            'change_email': reverse('misago:api:user-change-email', kwargs={'pk': obj.pk}),
            'change_password': reverse('misago:api:user-change-password', kwargs={'pk': obj.pk}),
        }


AuthenticatedUserSerializer = AuthenticatedUserSerializer.exclude_fields(
    'is_avatar_locked',
    'is_blocked',
    'is_followed',
    'is_signature_locked',
    'meta',
    'signature',
    'status',
)


class AnonymousUserSerializer(serializers.Serializer, AuthFlags):
    id = serializers.ReadOnlyField()
    acl = serializers.SerializerMethodField()
    is_authenticated = serializers.SerializerMethodField()
    is_anonymous = serializers.SerializerMethodField()

    def get_acl(self, obj):
        if hasattr(obj, 'acl_cache'):
            return serialize_acl(obj)
        else:
            return {}
