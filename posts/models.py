from django.conf import settings
from django.db import models


class Hashtag(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True)

    def save(self, *args, **kwargs):
        self.name = self.name or "".lower()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"#{self.name}"


class Post(models.Model):
    class Status(models.TextChoices):
        PUBLISHED = "published", "Published"
        SCHEDULED = "scheduled", "Scheduled"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    content = models.TextField()
    hashtags = models.ManyToManyField(Hashtag, blank=True, related_name="posts")

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PUBLISHED
    )
    scheduled_for = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["author", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"Post({self.id}) by {self.author_id}"
