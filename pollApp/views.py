from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required, user_passes_test


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
    return render(request, 'activePolls.html')


def archivedPolls(request):
    return render(request, 'archivePolls.html')
