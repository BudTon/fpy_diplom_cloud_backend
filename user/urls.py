from os import path

from rest_framework.routers import DefaultRouter

from django.contrib.auth import views as auth_views  # noqa: F401

from django.urls import (
    path,  # noqa: F811
    include,
)

from .views import (
    FileViewSet,
    UserAdmin,
    UserViewSet,
    user_login,
    StorageView,
    RegistrationView,
    StorageViewPatch,
    DownloadFileView,
    download_file_link,
)


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
    path(
        "download/file/<int:file_id>/",
        DownloadFileView.as_view(),
        name="download_file",
    ),
    path("user/<int:user_id>/", UserAdmin.as_view(), name="user_list"),
    path(
        "download/file/<uuid:short_hash>/<str:action>",
        download_file_link,
        name="download_file_link",
    ),
    path("", include(router.urls)),
]
