from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from project.models import Saved
from users.forms import LoginForm, RegistrationForm, CustomPasswordResetForm, CustomSetPasswordForm, ProfileForm
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView

from users.models import Profile


class CustomLoginView(LoginView):
    authentication_form = LoginForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация на сайте'}

    def get_success_url(self):
        return reverse_lazy('home')


def logoutUser(request):
    logout(request)
    messages.info(request, 'Вы вышли из учетной записи')
    return redirect('home')

def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'users/signup.html', {'form': form})



@login_required(login_url='login')
def profile(request):
    profile = ProfileForm(instance=request.user)
    user_forecasts = Saved.objects.filter(user=request.user)
    context = {
        'profile': profile,
        'user_forecasts': user_forecasts,
    }
    return render(request, 'users/profile.html', context)



@login_required(login_url='login')
def editProfile(request):
    form = ProfileForm(instance=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    context = {'form': form}
    return render(request, 'users/edit.html', context)

