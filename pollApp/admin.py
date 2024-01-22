from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Poll, Option

admin.site.site_header = "Poll App"
admin.site.site_title = "Poll Admin Area"
admin.site.index_title = "Welcome to the Poll Admin Area"


class OptionInline(admin.TabularInline):
    model = Option
    extra = 0


class PollAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['title', 'quorum_type', 'quorum', 'time_option', 'start_option', 'active_time', 'start_time', 'end_time']}),
        ('Date Information', {'fields': ['created_at'], 'classes': ['collapse']}),
    ]
    inlines = [OptionInline]

    class Media:
        js = ('js/admin.js',)

admin.site.register(Poll, PollAdmin)
