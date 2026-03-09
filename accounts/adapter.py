from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse


class MyAccountAdapter(DefaultAccountAdapter):

    def get_signup_redirect_url(self, request):
        return reverse("account_login")

    def get_login_redirect_url(self, request):
        user = request.user

        if user.is_superuser:
            return "/admin/"

        return "/accounts/onboarding/"