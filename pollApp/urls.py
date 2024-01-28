from django.urls import path

from .utils.report_generator import generate_report

urlpatterns = [

    path('report/<int:poll_id>/', generate_report, name='generate_report'),
]