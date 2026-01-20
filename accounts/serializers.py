from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from rest_framework import serializers

from accounts.models import Follow, Profile

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "email", "username", "password")

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        Profile.objects.get_or_create(user=user)

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("User is inactive")
        attrs["user"] = user
        return attrs


class UserPublicSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id", "email")


class ProfileReadSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            "user",
            "bio",
            "image",
            "website",
            "location",
            "created_at",
            "updated_at",
        )


class ProfileUpdateSerializer(serializers.Serializer):

    class Meta:
        model = Profile
        fields = ("bio", "avatar", "website", "location")


class FollowCreateSerializer(serializers.Serializer):
    def validate(self, attrs):
        request = self.context["request"]
        target_user = self.context["target_user"]

        if request.user == target_user:
            raise serializers.ValidationError("You can't follow yourself.")
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        target_user = self.context["target_user"]
        follow, _ = Follow.objects.get_or_create(
            follower=request.user, following=target_user
        )
        return follow
