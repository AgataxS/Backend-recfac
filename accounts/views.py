import base64
import numpy as np
import face_recognition
import cv2

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()

class UserListView(generics.ListCreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated] 
    # Requiere token para ver a los usuarios

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
class RegisterView(generics.CreateAPIView):
    """
    Crea un usuario con email, username y password (sin foto).
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class UpdateFaceAndImageView(APIView):
    """
    Permite que un usuario autenticado suba su imagen (base64) para generar y
    almacenar el encoding facial (y opcionalmente la foto).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        image_data = request.data.get('image', None)
        if not image_data:
            return Response({"detail": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decodificar base64 -> bytes
            img_bytes = base64.b64decode(image_data)
        except Exception:
            return Response({"detail": "Error decoding base64"}, status=status.HTTP_400_BAD_REQUEST)

        # Convertir a np array y luego a imagen con OpenCV
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return Response({"detail": "Invalid image"}, status=status.HTTP_400_BAD_REQUEST)

        # Extraer encoding
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_img)
        if not encodings:
            return Response({"detail": "No face detected"}, status=status.HTTP_400_BAD_REQUEST)

        encoding = encodings[0]
        # Convertir encoding a string
        encoding_str = ' '.join(map(str, encoding.tolist()))

        user = request.user
        user.face_encoding = encoding_str

        # (Opcional) si quieres guardar la foto en profile_image:
        # from django.core.files.base import ContentFile
        # file_obj = ContentFile(img_bytes, name='profile_image.jpg')
        # user.profile_image.save('profile_image.jpg', file_obj, save=False)

        user.save()
        return Response({"detail": "Face encoding updated"}, status=status.HTTP_200_OK)


class FacialLoginView(APIView):
    """
    Recibe una imagen base64, obtiene su encoding y lo compara con los de la BD.
    Si coincide, responde con tokens JWT.
    """
    def post(self, request):
        image_data = request.data.get('image', None)
        if not image_data:
            return Response({"detail": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            img_bytes = base64.b64decode(image_data)
        except Exception:
            return Response({"detail": "Error decoding base64"}, status=status.HTTP_400_BAD_REQUEST)

        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return Response({"detail": "Invalid image"}, status=status.HTTP_400_BAD_REQUEST)

        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_img)
        if not encodings:
            return Response({"detail": "No face detected"}, status=status.HTTP_400_BAD_REQUEST)

        current_encoding = encodings[0]
        # Buscar en la BD
        users = User.objects.exclude(face_encoding__isnull=True).exclude(face_encoding='')

        for user in users:
            user_vector = np.fromstring(user.face_encoding, sep=' ')
            match = face_recognition.compare_faces([user_vector], current_encoding, tolerance=0.6)
            if match[0]:
                # Generar tokens JWT
                refresh = RefreshToken.for_user(user)
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user_id": user.id,
                    "email": user.email,
                    "username": user.username
                }, status=status.HTTP_200_OK)

        return Response({"detail": "No match found"}, status=status.HTTP_401_UNAUTHORIZED)
