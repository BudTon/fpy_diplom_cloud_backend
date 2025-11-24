import json
import mimetypes
import os
from django.http import FileResponse, HttpResponse, JsonResponse
from rest_framework.viewsets import ModelViewSet
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from util.generate_download_link import generate_download_link
from user.serializers import FileSerializer, UserSerializer
from user.models import File
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

# from util.mime_to_extension import mime_to_extension
from django.core.files.storage import default_storage
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class FileViewSet(ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer


# @api_view(["GET"])
# @permission_classes([AllowAny])  # Позволяет доступ без аутентификации
def download_file_link(request, short_hash, action):
    print("-----------------------")
    print("download_file:", f"{request}")
    print("download_file:", f"{short_hash}")
    print("action:", action)
    print("-----------------------")

    uploaded_file = get_object_or_404(File, short_hash=short_hash)
    print("uploaded_file.type:", uploaded_file.type)

    if action.lower() == "view":
        disposition = "inline"
        response = FileResponse(
            uploaded_file.file.open(), content_type=uploaded_file.type
        )
    else:
        disposition = "attachment"
        response = FileResponse(
            uploaded_file.file.open(), content_type="application/octet-stream"
        )
        uploaded_file.lastDownloadDate = timezone.now()
        uploaded_file.save()

    response["Content-Disposition"] = (
        f'{disposition}; filename="{uploaded_file.file_name}"'
    )
    return response


@csrf_exempt
def user_login(request):
    print("-----------------------")
    print(f"Метод reques: {request.method}")
    print("-----------------------")

    if request.method != "POST":
        return JsonResponse({"error": "Method Not Allowed"}, status=405)

    # Читаем raw body запроса
    body_unicode = request.body.decode("utf-8")
    body_data = json.loads(body_unicode)

    # Достаем username и password
    username = body_data.get("username")
    password = body_data.get("password")

    print("username:", username)
    print("password:", password)

    # Проверяем аутентификацию
    user = authenticate(request, username=username, password=password)
    print("user:", user)

    if user is not None:
        login(request, user)
        print(user.id, " - request")
        token, created = Token.objects.get_or_create(user=user)
        return JsonResponse(
            {
                "token": token.key,
                "status": "ok",
                "userId": user.id,
                "isStaff": user.is_staff,
            }
        )
    else:
        return JsonResponse(
            {"status": "error", "message": "Invalid credentials."}, status=401
        )


class UserAdmin(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id):
        """
        PATCH-запрос для изменения метаданных файла
        :param request: объект запроса
        :param file_id: ID файла для изменения
        """
        print("-------------------------")
        print("        UserAdmin        def patch(self, request, user_id):")
        print("--------- REQUEST DETAILS !patch!---------")
        print("METHOD:", request.method)
        print("QUERY pk:", user_id)
        print("QUERY USER:", request.user)
        print("QUERY data:", request.data)
        print("----------- END OF REQUEST ----------")

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Пользаватель не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        new_is_staff = request.data.get("newIsStaff", user.is_staff)
        print(new_is_staff, " - new_is_staff")
        user.is_staff = new_is_staff
        user.save()
        return Response(
            {"detail": "Метаданные пользователя успешно обновлены"},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, user_id):
        """
        DELETE-запросы для удаления файла по id
        :param request: объект запроса
        :param pk: ID файла для удаления
        """
        print("-------------------------")

        print("        UserAdmin        def delete(self, request, user_id):")
        print("--------- REQUEST DETAILS ---------")
        print("METHOD:", request.method)
        print("QUERY pk:", user_id)
        print("QUERY USER:", request.user)
        print("----------- END OF REQUEST ----------")

        try:
            user_delete = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Пользаватель не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        if request.method == "DELETE" and request.user.is_authenticated:
            files_delete = File.objects.filter(user=user_delete)
            if files_delete:
                for file_del in files_delete:
                    path_to_file = file_del.file.path
                    default_storage.delete(path_to_file)
                File.objects.filter(user=user_delete).delete()
            user_delete.delete()

            return Response(
                {"status": "ok", "message": "Файл успешно удален!"}, status=204
            )

        return Response(
            {"status": "error", "message": "Метод не поддерживается."}, status=404
        )


class StorageViewPatch(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, file_id):
        """
        PATCH-запрос для изменения метаданных файла
        :param request: объект запроса
        :param file_id: ID файла для изменения
        """
        print("-------------------------")
        print("        StorageViewPatch        def patch(self, request, file_id):")
        print("--------- REQUEST DETAILS !patch!---------")
        print("METHOD:", request.method)
        print("QUERY pk:", file_id)
        print("QUERY USER:", request.user)
        print("QUERY data:", request.data)
        print("----------- END OF REQUEST ----------")

        try:
            file = File.objects.get(pk=file_id)
        except File.DoesNotExist:
            return Response(
                {"detail": "Файл не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        # Обновляем метаданные файла
        new_file_name = request.data.get("newFileName", file.file_name)
        print(new_file_name, " - new_file_name")
        new_comment = request.data.get("newComment", file.comment)
        print(new_comment, " - newComment")

        # Обновляем файл
        file.file_name = new_file_name
        file.comment = new_comment
        file.save()

        return Response(
            {"detail": "Метаданные файла успешно обновлены"}, status=status.HTTP_200_OK
        )


class StorageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print("-------------------------")
        print("        StorageView        def get(self, request):")
        print("--------- REQUEST DETAILS ---------")
        print("METHOD:", request.method)
        print("QUERY PARAMETERS:", dict(request.GET))
        print("----------- END OF REQUEST ----------")
        print(f"Is staff: {request.user.is_staff}")
        print(f"request.user: {request.user.id}")

        user_id = request.query_params.get("user_id", None)

        if request.user.is_authenticated:
            target_user = None

            if user_id is not None:
                try:
                    target_user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    return Response(
                        {
                            "status": "error",
                            "message": f"User with ID '{user_id}' does not exist.",
                        },
                        status=404,
                    )
            else:
                target_user = request.user

            # elif not request.user.is_staff:
            #     target_user = request.user

            if target_user is not None:
                user_files = list(File.objects.filter(user=target_user).values())
            else:
                user_files = []

            if request.user.is_staff:
                users = User.objects.all()
                user_serializer = UserSerializer(users, many=True).data
                for user_data in user_serializer:
                    files = File.objects.filter(user=user_data["id"])
                    user_data["total_size"] = sum(file.file.size for file in files)
                    user_data["file_count"] = len(files)
            else:
                user_serializer = []
            print("target_user:", target_user.id)
            return Response(
                {
                    "status": "ok",
                    "message": "Successfully retrieved storage information.",
                    "user_name": str(target_user),
                    "userId": target_user.id,
                    "user_files": user_files,
                    "users": user_serializer,
                }
            )
        else:
            return Response(
                {"status": "error", "message": "Invalid credentials."}, status=401
            )

    def post(self, request):
        print("-------------------------")
        print("        StorageView")
        print("        def post(self, request):")
        print("--------- REQUEST DETAILS ---------")
        print("METHOD:", request.method)
        print("QUERY PARAMETERS:", dict(request.GET))
        print("QUERY USER:", request.user)
        print("----------- END OF REQUEST ----------")
        print(request.data)
        if request.method == "POST":
            file_obj = request.FILES.get("file")
            user_storage = request.POST.get("user_storage")
            user = User.objects.get(username=user_storage)
            if file_obj:
                file_name = file_obj.name
                # file_type = mime_to_extension(file_obj.content_type)
                file_type = file_obj.content_type
                file_size = file_obj.size
                comment = request.POST.get("comment")
                uploaded_file = File(
                    user=user,
                    file_name=file_name,
                    type=file_type,
                    file=file_obj,
                    size=file_size,
                    comment=comment,
                )
                uploaded_file.save()
                file_links = generate_download_link(request, uploaded_file)
                uploaded_file.links = file_links
                uploaded_file.save()
                return JsonResponse({"message": "Файл успешно загружен!"})
            else:
                return JsonResponse({"error": "Файл не найден."}, status=400)
        return JsonResponse({"error": "Метод не поддерживается."}, status=405)

    def delete(self, request, pk=None):
        """
        DELETE-запросы для удаления файла по id
        :param request: объект запроса
        :param pk: ID файла для удаления
        """
        print("-------------------------")
        print("--------- REQUEST DETAILS ---------")
        print("METHOD:", request.method)
        print("QUERY pk:", pk)
        print("QUERY USER:", request.user)
        print("----------- END OF REQUEST ----------")

        user_id = request.GET.get("user_id")
        target_user = User.objects.get(id=user_id)
        file_id = request.GET.get("file_id")

        print("QUERY user_id:", user_id)
        print("QUERY file_id:", file_id)
        print("QUERY target_user:", target_user)

        if request.method == "DELETE" and request.user.is_authenticated:
            file_instance = File.objects.get(id=file_id, user=target_user)
            print("file_instance:", file_instance)
            path_to_file = file_instance.file.path
            default_storage.delete(path_to_file)
            file_instance.delete()
            return Response(
                {"status": "ok", "message": "Файл успешно удален!"}, status=204
            )
        return Response(
            {"status": "error", "message": "Метод не поддерживается."}, status=404
        )


class DownloadFileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        print("-------------------------")
        print("        DownloadFileView")
        print("        def get(self, request, file_id):")
        print("--------- REQUEST DETAILS download---------")
        print("METHOD:", request.method)
        print("QUERY pk:", file_id)
        print("QUERY USER:", request.user)
        print("----------- END OF REQUEST ----------")

        try:
            file = File.objects.get(pk=file_id)
        except File.DoesNotExist:
            return Response(
                {"detail": "Файл не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        file_path = file.file.path
        content_type, _ = mimetypes.guess_type(file_path)
        response = HttpResponse(content_type=content_type)
        response["Content-Length"] = os.path.getsize(file_path)
        response["Content-Disposition"] = f'attachment; filename="{file.file_name}"'

        with open(file_path, "rb") as fh:
            response.write(fh.read())
        print(response, " - response")
        file.lastDownloadDate = timezone.now()
        file.save()
        return response


class RegistrationView(APIView):
    authentication_classes = []  # Отключаем проверку токена
    permission_classes = []  # Разрешаем всем пользователям регистрироваться

    def post(self, request):
        username = request.data.get("username")
        first_name = request.data.get("firstname")
        email = request.data.get("email")
        password = request.data.get("password")
        is_staff = request.data.get("is_staff")
        print(
            "username: ",
            username,
            "\n",
            "firstname: ",
            first_name,
            "\n",
            "email: ",
            email,
            "\n",
            "password: ",
            password,
            "\n",
            "is_staff: ",
            is_staff,
        )
        if not all([username, first_name, email, password]):
            return Response(
                {
                    "error": "Все поля обязательны",
                    "request_data": {
                        "username": username,
                        "firstname": first_name,
                        "email": email,
                        "password": password,
                        "is_staff": is_staff,
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                email=email,
                password=password,
                is_staff=is_staff,
            )
            return Response(
                {"message": f"Пользователь {user.username} успешно зарегистрирован"},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
