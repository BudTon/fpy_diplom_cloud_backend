from user.serializers import UserSerializer
from user.models import File
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView


class HomeView(APIView):
    authentication_classes = []
    permission_classes = []  # noqa: F811

    def get(self, request):
        users = User.objects.all()
        users_total = UserSerializer(users, many=True).data
        user_total_count = len(users_total)
        files_total = File.objects.all()
        files_total_count = len(files_total)
        files_total_size = sum(file.file.size for file in files_total)

        return Response(
            {
                "status": "ok",
                "message": "Successfully retrieved storage information.",
                "totalUsers": user_total_count,
                "totalFiles": files_total_count,
                "totalSize": files_total_size,
            }
        )
