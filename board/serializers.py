from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import Sprint, Task

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)
    links = serializers.SerializerMethodField("get_links")

    class Meta:
        model = User
        fields = ("id", User.USERNAME_FIELD, "full_name", "is_active", "links")

    def get_links(self, obj):
        request = self.context["request"]
        username = obj.get_username()
        return {
            "self": reverse(
                "user-detail", kwargs={User.USERNAME_FIELD: username}, request=request
            )
        }


class SprintSerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField("get_links")

    class Meta:
        model = Sprint
        fields = ("id", "name", "description", "end", "links")

    def get_links(self, obj):
        request = self.context["request"]
        return {
            "self": reverse("sprint-detail", kwargs={"pk": obj.pk}, request=request),
            "tasks": reverse("task-list", request=request) + f"?sprint={obj.pk}",
        }

    def validate_end(self, end_date):
        new = not self.instance
        changed = self.instance and self.instance.end != end_date
        if (new or changed) and (end_date < timezone.now().date()):
            msg = _("End Date cannot be in the past.")
            raise serializers.ValidationError(msg)
        return end_date


class TaskSerializer(serializers.ModelSerializer):
    assigned = serializers.SlugRelatedField(
        slug_field=User.USERNAME_FIELD, read_only=True, required=False
    )
    status_display = serializers.SerializerMethodField("get_status_display")
    links = serializers.SerializerMethodField("get_links")

    class Meta:
        model = Task
        fields = (
            "id",
            "name",
            "description",
            "sprint",
            "status",
            "order",
            "assigned",
            "started",
            "due",
            "completed",
            "status_display",
            "links",
        )

    def get_status_display(self, obj: Task):
        return obj.get_status_display()

    def get_links(self, obj: Task):
        links = {
            "self": reverse(
                "task-detail", kwargs={"pk": obj.pk}, request=self.context["request"]
            ),
            "sprint": None,
            "assigned": None,
        }

        if obj.sprint_id:
            links["sprint"] = reverse(
                "sprint-detail",
                kwargs={"pk": obj.sprint_id},
                request=self.context["request"],
            )
        if obj.assigned:
            links["assigned"] = reverse(
                "user-detail",
                kwargs={User.USERNAME_FIELD: obj.assigned},
                request=self.context["request"],
            )

        return links

    def validate_sprint(self, sprint):
        if self.instance and self.instance.pk:
            if sprint != self.instance.sprint:
                if self.instance.status == Task.STATUS_DONE:
                    msg = _("Cannot change the sprint of a completed task.")
                    raise serializers.ValidationError(msg)
                if sprint and sprint.end < timezone.now().date():
                    msg = _("Cannot assign tasks to past sprints.")
                    raise serializers.ValidationError(msg)
            else:
                if sprint and sprint.end < timezone.now().date():
                    msg = _("Cannot add tasks to past sprints.")
                    raise serializers.ValidationError(msg)
            return sprint

    def validate(self, attrs):
        super().validate(attrs)
        sprint = attrs.get("sprint")
        status = attrs.get("status")
        started = attrs.get("started")
        completed = attrs.get("completed")
        msg = None

        if not sprint and status != Task.STATUS_TODO:
            msg = _("Backlog tasks must have 'Not Started' status.")
        if started and status == Task.STATUS_TODO:
            msg = _("Started date cannot be set for not started tasks.")
        if completed and status != Task.STATUS_DONE:
            msg = _("Completed date cannot be set for uncompleted tasks.")
        if status == Task.STATUS_DONE and not completed:
            msg = _("Completed date cannot be empty for completed tasks.")
        if msg:
            raise serializers.ValidationError(msg)
        return attrs
