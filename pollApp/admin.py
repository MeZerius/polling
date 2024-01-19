from django.contrib import admin
from .models import Poll, Option


admin.site.site_header = "Poll App"
admin.site.site_title = "Poll Admin Area"
admin.site.index_title = "Welcome to the Poll Admin Area"


class OptionInline(admin.TabularInline):
    model = Option
    extra = 2


class PollAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['title', 'quorum', 'active_time']}),
        ('Date Information', {'fields': ['created_at'], 'classes': ['collapse']}),
    ]
    inlines = [OptionInline]


admin.site.register(Poll, PollAdmin)