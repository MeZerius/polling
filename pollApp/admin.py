from django.contrib import admin
from django import forms
from django.urls import path, include
from django.utils.html import format_html
from django.forms.widgets import CheckboxInput
from django.http import FileResponse
import os
import tempfile
from django.core.files.base import ContentFile
from zipfile import ZipFile
from .models import Poll, Option
from .utils.report_generator import generate_report

admin.site.site_header = "Poll App"
admin.site.site_title = "Poll Admin Area"
admin.site.index_title = "Welcome to the Poll Admin Area"


class OptionInline(admin.TabularInline):
    model = Option
    extra = 0


class CustomCheckbox(CheckboxInput):
    def render(self, name, value, attrs=None, renderer=None):
        final_attrs = self.build_attrs(self.attrs, attrs)
        return format_html('<label>{} <input type="checkbox" name="{}" value="{}" style="margin-left: 10px;" {}></label>',
                           name.capitalize(), name, value,
                           'checked' if value else '')

class PollForm(forms.ModelForm):
    majority = forms.BooleanField(required=False, widget=CustomCheckbox(), label='')

    class Meta:
        model = Poll
        fields = '__all__'


class PollAdmin(admin.ModelAdmin):
    form = PollForm
    fieldsets = [
        (None, {'fields': ['title', 'majority', 'quorum_type', 'quorum', 'time_option', 'start_option', 'active_time',
                           'start_time', 'end_time']}),
        ('Date Information', {'fields': ['created_at'], 'classes': ['collapse']}),
    ]
    inlines = [OptionInline]
    actions = ['generate_report_action']

    class Media:
        js = ('js/admin.js',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creator = request.user
        super().save_model(request, obj, form, change)


    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('report/<int:poll_id>/', generate_report, name='generate_report'),
        ]
        return urls + my_urls

    def generate_report(self, request, poll_id):
        return generate_report(request, poll_id)

    def generate_report_action(self, request, queryset):
        if len(queryset) == 1:
            # If there's only one poll, generate the report and return it directly
            return generate_report(request, queryset[0].id)
        else:
            # If there's more than one poll, generate reports for all and pack them into an archive
            with tempfile.TemporaryDirectory() as tmpdirname:
                for poll in queryset:
                    response = generate_report(request, poll.id)
                    report_file = os.path.join(tmpdirname, f'poll_{poll.id}_report.pdf')
                    with open(report_file, 'wb') as f:
                        f.write(response.getvalue())

                # Create a zip file
                zip_file_path = os.path.join(tmpdirname, 'poll_reports.zip')
                with ZipFile(zip_file_path, 'w') as zipf:
                    for file in os.listdir(tmpdirname):
                        if file.endswith('.pdf'):
                            zipf.write(os.path.join(tmpdirname, file), arcname=file)

                # Read the zip file and create a FileResponse
                with open(zip_file_path, 'rb') as f:
                    content = f.read()

                response = FileResponse(ContentFile(content), as_attachment=True, filename='poll_reports.zip')
                response['Content-Disposition'] = 'attachment; filename=poll_reports.zip'
                return response

    generate_report_action.short_description = 'Generate PDF Report'


admin.site.register(Poll, PollAdmin)
