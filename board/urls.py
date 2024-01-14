from rest_framework import routers

from .views import SprintViewSet, UserViewSet, TaskViewSet

router = routers.DefaultRouter()
router.register("sprints", SprintViewSet)
router.register("tasks", TaskViewSet)
router.register("users", UserViewSet)
