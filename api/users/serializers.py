from rest_framework import serializers

from api.users.models import User
from main.serilaizer import DynamicFieldsModelSerializer


class AuthenticateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, allow_blank=False, allow_null=False)
    password = serializers.CharField(required=True, allow_blank=False, allow_null=False)

    class Meta:
        model = User
        fields = ('email', 'password')


class UserSerializer(DynamicFieldsModelSerializer):
    email = serializers.EmailField(required=True, allow_null=False, allow_blank=False)
    is_active = serializers.BooleanField(read_only=True)
    first_name = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    is_email_verified = serializers.BooleanField(read_only=True)
    events = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', "is_active", 'is_email_verified', "events")

    def create(self, validated_data):
        user = User.objects.create(
            **validated_data,
            is_active=True,
            is_approved=True
        )
        return user

    def get_events(self,obj):
        return obj.event_user.count()

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance
