from django.urls import include, path
from rest_framework.routers import DefaultRouter

from interactions.views import LikeViewSet, CommentViewSet


router = DefaultRouter()
router.register("post-actions", LikeViewSet, basename="post-actions")
router.register("comments", CommentViewSet, basename="comments")
urlpatterns = [path("", include(router.urls))]

app_name = "interactions"
