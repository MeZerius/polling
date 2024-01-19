from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, LoginForm, OptionForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, OuterRef, Exists

from django.utils import timezone

from .models import Poll, Option


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


def pollPage(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    poll.total_votes = sum(option.votes.count() for option in poll.options.all())
    form = OptionForm()  # Define form before the if condition
    user_has_voted = poll.has_user_voted(request.user) if request.user.is_authenticated else False
    if request.method == 'POST':
        option_id = request.POST.get('option')
        option = poll.options.get(id=option_id)
        if not poll.is_expired and not user_has_voted:
            option.votes.add(request.user)
            return redirect('pollPage', poll_id=poll.id)

    options = poll.options.all().annotate(
        user_has_voted_for_option=Exists(
            Option.votes.through.objects.filter(
                option_id=OuterRef('id'),
                user_id=request.user.id if request.user.is_authenticated else None
            )
        )
    )
    return render(request, 'pollPage.html',
                  {'poll': poll, 'form': form, 'user_has_voted': user_has_voted, 'options': options})