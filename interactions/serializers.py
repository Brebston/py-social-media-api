from rest_framework import serializers
from interactions.models import Comment, Like


class CommentReadSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "post", "author", "text", "parent", "created_at", "updated_at")

    def get_author(self, obj):
        return {"id": obj.author_id, "username": getattr(obj.author, "username", None)}


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("text", "parent")

    def validate(self, attrs):
        if not (attrs.get("text") or "").strip():
            raise serializers.ValidationError({"text": "Comment cannot be empty."})
        return attrs


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "user", "post", "created_at")
        read_only_fields = ("id", "user", "created_at")
