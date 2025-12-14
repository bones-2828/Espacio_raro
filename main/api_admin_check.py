from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


class AdminOnlyCheckAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            return Response(
                {"detail": "No es superusuario"},
                status=status.HTTP_403_FORBIDDEN
            )

        return Response(
            {
                "username": request.user.username,
                "is_superuser": True
            },
            status=status.HTTP_200_OK
        )


