from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User



class AdminLoginAPIView(APIView):   
    authentication_classes = []
    permission_classes = []


    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "Debe ingresar usuario y contraseña."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"detail": "Credenciales inválidas."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.is_superuser:
            return Response(
                {"detail": "Acceso denegado. Requiere permisos de superusuario."},
                status=status.HTTP_403_FORBIDDEN
            )


        token, created = Token.objects.get_or_create(user=user)


        return Response(
            {
                "token": token.key,
                "username": user.username,
                "is_superuser": user.is_superuser
            },
            status=status.HTTP_200_OK
        )


