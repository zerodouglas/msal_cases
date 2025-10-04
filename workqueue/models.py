
from django.conf import settings
from django.db import models
from django.utils import timezone

SEVERITY_CHOICES = (
    (1, "Low"),
    (2, "Moderate"),
    (3, "Elevated"),
    (4, "High"),
    (5, "Critical"),
)

class Officer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return self.display_name or self.user.get_username()

class Case(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    severity = models.IntegerField(choices=SEVERITY_CHOICES, default=3)
    assigned_officer = models.ForeignKey(
        Officer, null=True, blank=True, on_delete=models.SET_NULL, related_name="cases"
    )
    assigned_at = models.DateTimeField(default=timezone.now)

    # Policy: reports due within 10 days, unless DA-specific due date applies
    going_to_da = models.BooleanField(default=False)
    da_due_at = models.DateTimeField(null=True, blank=True)

    report_completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=(
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
        ),
        default="open",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def policy_due_at(self):
        # 10 days from assignment by policy
        return self.assigned_at + timezone.timedelta(days=10)

    @property
    def effective_due_at(self):
        if self.going_to_da and self.da_due_at:
            return min(self.da_due_at, self.policy_due_at)
        return self.policy_due_at

    def __str__(self):
        return f"Case #{self.id}: {self.title}"

class Report(models.Model):
    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name="report")
    drafted_by = models.ForeignKey(Officer, on_delete=models.SET_NULL, null=True)
    content = models.TextField(blank=True)
    submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Report for Case #{self.case_id}"
