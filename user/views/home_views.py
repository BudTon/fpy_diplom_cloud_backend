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
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

class HomeView(APIView):
    authentication_classes = []  # Отключаем проверку токена
    permission_classes = []  # Разрешаем всем пользователям получать доступ

    def get(self, request):
        print("-------------------------")
        print("        HomeView        def get(self, request):")
        print("--------- REQUEST DETAILS ---------")
        print("METHOD:", request.method)
        # print("QUERY PARAMETERS:", dict(request.GET))
        print("----------- END OF REQUEST ----------")
        users = User.objects.all()
        users_total = UserSerializer(users, many=True).data
        user_total_count = len(users_total)
        files_total = File.objects.all()
        files_total_count = len(files_total)
        files_total_size = sum(file.file.size for file in files_total)

        print("user_total_count: ", user_total_count)
        print("files_total_count: ", files_total_count)
        print("files_total_size: ", files_total_size)

        return Response(
            {
                "status": "ok",
                "message": "Successfully retrieved storage information.",
                "totalUsers": user_total_count,
                "totalFiles": files_total_count,
                "totalSize": files_total_size,
            }
        )
