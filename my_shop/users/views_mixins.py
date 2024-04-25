from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse


class UserNotAuthenticatedMixin(UserPassesTestMixin):
    def test_func(self):
        return not self.request.user.is_authenticated
    
    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_anonymous:
            return super(UserNotAuthenticatedMixin, self).handle_no_permission()
        return redirect('users:profile')
