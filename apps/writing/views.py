from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView

from apps.core.access import visible_projects
from apps.notifications.services import notify
from apps.research.models import Chapter

from .forms import ChapterDraftForm
from .models import ChapterDraft

EDITABLE_STATUSES = {Chapter.Status.DRAFT, Chapter.Status.REVISION}


class WritingIndexView(LoginRequiredMixin, ListView):
    template_name = "writing/index.html"
    context_object_name = "chapters"

    def get_queryset(self):
        return (
            Chapter.objects.filter(project__in=visible_projects(self.request.user))
            .select_related("project")
            .prefetch_related("drafts")
        )


@login_required
def chapter_edit(request, pk):
    chapter = get_object_or_404(
        Chapter.objects.select_related("project", "project__owner").filter(
            project__in=visible_projects(request.user)
        ),
        pk=pk,
    )
    is_owner = chapter.project.owner_id == request.user.id
    draft = chapter.drafts.first()
    reviews = chapter.reviews.select_related("reviewer")

    if request.method == "POST":
        if not is_owner:
            raise PermissionDenied("Only the chapter owner can edit this chapter.")
        if chapter.status == Chapter.Status.APPROVED:
            raise PermissionDenied("Approved chapters cannot be edited.")

        form = ChapterDraftForm(request.POST)
        action = request.POST.get("action", "save")
        if action not in {"save", "submit"}:
            messages.error(request, "Unknown action.")
            return redirect("writing:chapter_edit", pk=chapter.pk)

        if form.is_valid():
            content = form.cleaned_data["content"]
            if action == "submit" and not content.strip():
                form.add_error(
                    "content", "Write something before submitting for review."
                )
            else:
                is_resubmission = chapter.status == Chapter.Status.REVISION
                with transaction.atomic():
                    locked = Chapter.objects.select_for_update().get(pk=chapter.pk)
                    if action == "submit" and locked.status == Chapter.Status.FOR_REVIEW:
                        messages.info(
                            request, "This chapter is already awaiting review."
                        )
                        return redirect("writing:chapter_edit", pk=chapter.pk)
                    if locked.status not in EDITABLE_STATUSES:
                        raise PermissionDenied(
                            "This chapter cannot be edited in its current state."
                        )

                    draft = (
                        locked.drafts.select_for_update()
                        .order_by("-updated_at")
                        .first()
                    )
                    if draft is None:
                        draft = ChapterDraft(
                            chapter=locked, author=request.user, version=1
                        )
                    draft.content = content
                    draft.author = request.user
                    if action == "submit":
                        draft.is_submitted = True
                        draft.submitted_at = timezone.now()
                        locked.status = Chapter.Status.FOR_REVIEW
                        locked.save(update_fields=["status", "updated_at"])
                    else:
                        draft.is_submitted = False
                    draft.save()

                    if action == "submit" and locked.project.adviser_id:
                        verb = "resubmitted" if is_resubmission else "submitted"
                        notify(
                            locked.project.adviser,
                            f"{request.user.username} {verb} {locked} for review.",
                            reverse("teacher_submissions")
                            + f"?chapter={locked.pk}",
                        )

                messages.success(
                    request,
                    "Chapter resubmitted for review."
                    if action == "submit"
                    else "Draft saved.",
                )
                return redirect("writing:chapter_edit", pk=chapter.pk)
    else:
        form = ChapterDraftForm(instance=draft)

    return render(
        request,
        "writing/chapter_edit.html",
        {
            "chapter": chapter,
            "form": form,
            "draft": draft,
            "reviews": reviews,
            "is_owner": is_owner,
            "can_edit": is_owner and chapter.status in EDITABLE_STATUSES,
            "is_resubmission": chapter.status == Chapter.Status.REVISION,
        },
    )
