from datetime import timedelta

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
    polls = [poll for poll in Poll.objects.all() if
             (poll.start_time is None or poll.start_time <= now) and
             (poll.end_time is None or poll.end_time > now) and
             not poll.is_expired]
    for poll in polls:
        poll.total_votes = sum(option.votes.count() for option in poll.options.all())

        if poll.end_time is None:
            if poll.active_time is not None:
                if poll.start_time is not None:
                    poll.end_time = poll.start_time + poll.active_time
                else:
                    poll.end_time = poll.created_at + poll.active_time

    paginator = Paginator(polls, 9)
    page_number = request.GET.get('page')
    polls = paginator.get_page(page_number)
    return render(request, 'activePolls.html', {'polls': polls})


def archivedPolls(request):
    now = timezone.now()
    polls = [poll for poll in Poll.objects.all() if
             poll.is_expired or
             (
                     poll.start_time is not None and poll.active_time is not None and poll.start_time + poll.active_time < now) or
             (poll.end_time is not None and poll.end_time < now)]
    for poll in polls:
        poll.total_votes = sum(option.votes.all().count() for option in poll.options.all())
        poll.status = "Quorum isn't achieved" if poll.is_invalid else 'Expired'

    paginator = Paginator(polls, 9)
    page_number = request.GET.get('page')
    polls = paginator.get_page(page_number)
    return render(request, 'archivePolls.html', {'polls': polls}, )


def upcomingPolls(request):
    polls = [poll for poll in Poll.objects.all() if poll.start_time is not None and poll.start_time > timezone.now()]

    paginator = Paginator(polls, 9)
    page_number = request.GET.get('page')
    polls = paginator.get_page(page_number)

    return render(request, 'upcomingPolls.html', {'polls': polls})


def pollPage(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    poll.total_votes = sum(option.votes.count() for option in poll.options.all())
    form = OptionForm()
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

    now = timezone.now()
    end_time = None

    if poll.end_time is None:
        if poll.active_time is not None:
            if poll.start_time is not None:
                end_time = poll.start_time + poll.active_time
            else:
                end_time = poll.created_at + poll.active_time
    else:
        end_time = poll.end_time

    if poll.start_time is not None and poll.start_time > now:
        poll_status = "Upcoming"
        remaining_time = "Starts at: " + str(poll.start_time)
    else:
        remaining_time = end_time - now
        if remaining_time.total_seconds() > 0:
            remaining_time = str(timedelta(seconds=remaining_time.total_seconds()))
            poll_status = "Quorum isn't achieved" if poll.is_invalid else 'Active'
        else:
            remaining_time = "Poll has ended"
            poll_status = "Quorum isn't achieved" if poll.is_invalid else 'Expired'

    return render(request, 'pollPage.html',
                  {'poll': poll, 'form': form, 'user_has_voted': user_has_voted, 'options': options,
                   'remaining_time': remaining_time, 'poll_status': poll_status, 'end_time': end_time})
