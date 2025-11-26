from os import path

from rest_framework.routers import DefaultRouter

from django.contrib.auth import views as auth_views  # noqa: F401

from django.urls import (
    path,  # noqa: F811
    include,
)

from user.views.auth_views import user_login, RegistrationView
from user.views.file_views import FileViewSet, StorageViewPatch, download_file_link
from user.views.user_views import UserViewSet, UserAdmin
from user.views.storage_views import StorageView
# , DownloadFileView


router = DefaultRouter()
router.register("users", UserViewSet)
router.register("files", FileViewSet)


urlpatterns = [
    path("login/", user_login, name="login"),  # Ручная регистрация маршрута
    path("register/", RegistrationView.as_view(), name="register"),
    path("storage/", StorageView.as_view(), name="storage"),
    path("storage/<int:pk>", StorageView.as_view(), name="storage_detail"),
    path(
        "storage/patch/<int:file_id>/",
        StorageViewPatch.as_view(),
        name="storage_detail_patch",
    ),
    # path(
    #     "download/file/<int:file_id>/",
    #     DownloadFileView.as_view(),
    #     name="download_file",
    # ),
    path("user/<int:user_id>/", UserAdmin.as_view(), name="user_list"),
    path(
        "download/file/<uuid:short_hash>/<str:action>",
        download_file_link,
        name="download_file_link",
    ),
    path("", include(router.urls)),
]
