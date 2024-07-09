from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

urlpatterns = [
    path("auth/register/", views.RegisterAPI.as_view(), name="register"),
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("users/<int:pk>/", views.UserDetail.as_view(), name="user_detail"),
    path("organisations/", views.UserOrganizations.as_view(), name="organization_list"),
    path(
        "organisations/<str:orgId>/", views.get_organization, name="organization_detail"
    ),
    path("create-organization/", views.create_organization, name="create_org"),
    path(
        "organizations/<str:orgId>/users",
        views.add_user_to_organization,
        name="add_user_to_organization",
    ),
]
