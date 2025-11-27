import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import status


@csrf_exempt
def user_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method Not Allowed"}, status=405)
    body_unicode = request.body.decode("utf-8")
    body_data = json.loads(body_unicode)
    username = body_data.get("username")
    password = body_data.get("password")
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
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


class RegistrationView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get("username")
        first_name = request.data.get("firstname")
        email = request.data.get("email")
        password = request.data.get("password")
        is_staff = request.data.get("is_staff")
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
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
