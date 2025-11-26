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
from django.core.files.storage import default_storage
from django.utils import timezone
from django.shortcuts import get_object_or_404


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



# class DownloadFileView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request, file_id):
#         print("-------------------------")
#         print("        DownloadFileView")
#         print("        def get(self, request, file_id):")
#         print("--------- REQUEST DETAILS download---------")
#         print("METHOD:", request.method)
#         print("QUERY pk:", file_id)
#         print("QUERY USER:", request.user)
#         print("----------- END OF REQUEST ----------")

#         try:
#             file = File.objects.get(pk=file_id)
#         except File.DoesNotExist:
#             return Response(
#                 {"detail": "Файл не найден"}, status=status.HTTP_404_NOT_FOUND
#             )

#         file_path = file.file.path
#         content_type, _ = mimetypes.guess_type(file_path)
#         response = HttpResponse(content_type=content_type)
#         response["Content-Length"] = os.path.getsize(file_path)
#         response["Content-Disposition"] = f'attachment; filename="{file.file_name}"'

#         with open(file_path, "rb") as fh:
#             response.write(fh.read())
#         print(response, " - response")
#         file.lastDownloadDate = timezone.now()
#         file.save()
#         return response

