from django.http import FileResponse
from rest_framework.viewsets import ModelViewSet
from user.serializers import FileSerializer
from user.models import File
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.utils import timezone
from django.shortcuts import get_object_or_404


class FileViewSet(ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer


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
