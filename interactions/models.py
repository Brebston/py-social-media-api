from django.conf import settings
from django.db import models


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes"
    )
    post = models.ForeignKey(
        "posts.Post", on_delete=models.CASCADE, related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"], name="uniq_like_user_post"
            ),
        ]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["post", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"Like(u={self.user_id}, p={self.post_id})"


class Comment(models.Model):
    post = models.ForeignKey(
        "posts.Post", on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )

    text = models.TextField()
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["post", "created_at"]),
            models.Index(fields=["author", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"Comment({self.id})"
