from rest_framework.viewsets import ModelViewSet
from user.serializers import UserSerializer
from user.models import File
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.core.files.storage import default_storage


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


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
                {"detail": "Пользаватель не найден"},
                status=status.HTTP_404_NOT_FOUND
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
                {"status": "ok", "message": "Файл успешно удален!"},
                status=204
            )

        return Response(
            {"status": "error", "message": "Метод не поддерживается."},
            status=404
        )
