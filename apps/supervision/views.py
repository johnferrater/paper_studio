from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView

from .models import Supervision


class SupervisionListView(LoginRequiredMixin, ListView):
    model = Supervision
    template_name = "supervision/list.html"
    context_object_name = "supervisions"

    def get_queryset(self):
        return Supervision.objects.filter(
            Q(teacher=self.request.user) | Q(student=self.request.user)
        ).select_related("teacher", "student", "project")
