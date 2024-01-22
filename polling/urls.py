from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path
from django.conf import settings

import pollApp.views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', pollApp.views.index, name='index'),
    path('login/', pollApp.views.login, name='login'),
    path('register/', pollApp.views.register, name='register'),
    path('polls/active/', pollApp.views.activePolls, name='activePolls'),
    path('polls/archive/', pollApp.views.archivedPolls, name='archivedPolls'),
    path('polls/<int:poll_id>/', pollApp.views.pollPage, name='pollPage'),
    path('polls/upcoming/', pollApp.views.upcomingPolls, name='upcomingPolls'),

    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
