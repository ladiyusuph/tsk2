from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser

user = CustomUser


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    refresh["userId"] = user.userId
    refresh["email"] = user.email

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
