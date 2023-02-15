from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView)

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordChange(PasswordChangeView):
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_form.html'
    context = {'change': True}


class PasswordReset(PasswordResetView):
    success_url = reverse_lazy('users:password_reset_done')
    template_name = 'users/password_reset_form.html'
    context = {'reset': True}


class PasswordResetConfirm(PasswordResetConfirmView):
    success_url = reverse_lazy('users:password_reset_complete')
    template_name = 'users/password_reset_confirm.html'
