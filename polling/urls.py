from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path

import pollApp.views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', pollApp.views.index, name='index'),
    path('login/', pollApp.views.login, name='login'),
    path('register/', pollApp.views.register, name='register'),
    path('polls/active/', pollApp.views.activePolls, name='activePolls'),
    path('polls/archive/', pollApp.views.archivedPolls, name='archivedPolls'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),

]
