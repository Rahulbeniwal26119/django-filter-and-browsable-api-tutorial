from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Sprint(models.Model):
    """Developement iteration Period"""

    name = models.CharField(max_length=100, default="", blank=True)
    description = models.TextField(default="", blank=True)
    end = models.DateField(unique=True)

    def __str__(self):
        return self.name or _("Sprint ending {0}".format(self.end))


class Task(models.Model):
    STATUS_TODO = 1
    STATUS_IN_PROGRESS = 2
    STATUS_TESTING = 3
    STATUS_DONE = 4

    STATUS_CHOICES = (
        (STATUS_TODO, _("Not Started")),
        (STATUS_IN_PROGRESS, _("In Progress")),
        (STATUS_TESTING, _("Testing")),
        (STATUS_DONE, _("Done")),
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    sprint = models.ForeignKey(
        Sprint, null=True, on_delete=models.CASCADE
    )
    order = models.SmallIntegerField(default=0)
    assigned = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    started = models.DateField(blank=True, null=True)
    due = models.DateField(blank=True, null=True)
    completed = models.DateField(blank=True, null=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_TODO)

    def __str__(self):
        return self.name
    
    def get_status_display(self):
        return dict(self.STATUS_CHOICES)[self.status]
