from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count

from django.utils import timezone

from .models import Poll


def anonymous_required(user):
    return not user.is_authenticated


def index(request):
    return render(request, 'index.html')


@user_passes_test(anonymous_required, login_url='activePolls')
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('activePolls')
            else:
                form.add_error(None, "Invalid username or password")
        return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


@user_passes_test(anonymous_required, login_url='activePolls')
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('activePolls')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def activePolls(request):
    now = timezone.now()
    polls = [poll for poll in Poll.objects.all() if not poll.is_expired]
    for poll in polls:
        poll.total_votes = sum(option.votes.count() for option in poll.options.all())
        poll.end_time = poll.created_at + poll.active_time
    paginator = Paginator(polls, 9)
    page_number = request.GET.get('page')
    polls = paginator.get_page(page_number)
    return render(request, 'activePolls.html', {'polls': polls})


def archivedPolls(request):
    now = timezone.now()
    polls = [poll for poll in Poll.objects.all() if poll.is_expired]
    for poll in polls:
        poll.total_votes = sum(option.votes.all().count() for option in poll.options.all())
        poll.status = "Quorum isn't achieved" if poll.is_invalid else 'Expired'

    paginator = Paginator(polls, 9)
    page_number = request.GET.get('page')
    polls = paginator.get_page(page_number)
    return render(request, 'archivePolls.html', {'polls': polls})
