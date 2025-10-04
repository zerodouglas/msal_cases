from django.contrib import admin
from .models import Case, Officer, Report

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "severity", "going_to_da", "assigned_officer", "assigned_at", "status")
    list_filter = ("severity", "going_to_da", "status")
    search_fields = ("title", "description")

admin.site.register(Officer)
admin.site.register(Report)