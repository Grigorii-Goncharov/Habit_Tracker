from django.contrib import admin

from htracker.models import Habit


@admin.register(Habit)
class UserAdmin(admin.ModelAdmin):
    list_display = ("owner", "place", "time", "action", "pleasant_habit", "related_habit")
    search_fields = ("owner", "pleasant_habit")



