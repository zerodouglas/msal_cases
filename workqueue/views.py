from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from .models import Case, Officer, Report
from .priority import rank_cases
from .forms import CaseForm


def _ensure_officer(user):
    """Guarantee that each signed-in User has a linked Officer record."""
    officer, _ = Officer.objects.get_or_create(user=user)
    return officer


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    officer = _ensure_officer(request.user)
    qs = (
        Case.objects.filter(assigned_officer=officer)
        .exclude(status="completed")
        .select_related("assigned_officer")
    )
    ordered = rank_cases(qs)

    context = {
        "officer": officer,
        "cases": ordered,
        "now": timezone.now(),
    }
    return render(request, "workqueue/dashboard.html", context)


@login_required
def complete_report(request: HttpRequest, case_id: int) -> HttpResponse:
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    case = get_object_or_404(Case, id=case_id, assigned_officer__user=request.user)

    report, _ = Report.objects.get_or_create(
        case=case, defaults={"drafted_by": _ensure_officer(request.user)}
    )
    report.submitted = True
    report.submitted_at = timezone.now()
    report.save()

    case.status = "completed"
    case.report_completed_at = timezone.now()
    case.save(update_fields=["status", "report_completed_at"])

    messages.success(request, f"Case #{case.id} marked as completed.")
    return redirect("dashboard")


@method_decorator(login_required, name="dispatch")
class CaseCreateView(CreateView):
    """Form-based creation of new Cases, auto-assigned to the signed-in officer."""

    template_name = "workqueue/case_form.html"
    form_class = CaseForm
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        officer = _ensure_officer(self.request.user)
        obj = form.save(commit=False)
        obj.assigned_officer = officer
        obj.save()
        messages.success(self.request, f"Case #{obj.id} created.")
        return super().form_valid(form)
