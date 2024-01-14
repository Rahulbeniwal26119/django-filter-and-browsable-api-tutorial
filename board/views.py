from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, authentication, permissions, filters

from .forms import TaskFilter, SprintFilter
from .models import Sprint, Task
from .serializers import SprintSerializer, UserSerializer, TaskSerializer

User = get_user_model()


class DefaultMixin:
    authentication_classes = (
        authentication.BasicAuthentication,
        authentication.TokenAuthentication,
    )

    permission_classes = (permissions.IsAuthenticated,)

    paginate_by = 25
    paginate_by_param = "page_size"
    max_paginate_by = 100

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )


class SprintViewSet(DefaultMixin, viewsets.ModelViewSet):
    queryset = Sprint.objects.order_by("end")
    serializer_class = SprintSerializer
    search_fields = ("name",)
    ordering_fields = (
        "end",
        "name",
    )
    filterset_class = SprintFilter


class TaskViewSet(DefaultMixin, viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_class = TaskFilter
    search_fields = (
        "name",
        "description",
    )
    ordering_fields = (
        "name",
        "order",
        "started",
        "due",
        "completed",
    )

    # EG -> http://localhost:8000/api/tasks/?search=Task&ordering=-order


class UserViewSet(DefaultMixin, viewsets.ReadOnlyModelViewSet):
    lookup_field = User.USERNAME_FIELD
    lookup_url_kwarg = User.USERNAME_FIELD
    queryset = User.objects.order_by(User.USERNAME_FIELD)
    serializer_class = UserSerializer
    search_fields = (User.USERNAME_FIELD,)
