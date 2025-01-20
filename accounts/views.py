import base64
import numpy as np
import cv2
import face_recognition

from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    Crea un usuario con email, username y password.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class UpdateFaceAndImageView(APIView):
    """
    - Recibe una imagen base64 en 'image'
    - Extrae encoding facial y lo guarda en 'face_encoding'
    - Guarda la foto en 'profile_image'
    - Requiere autenticación JWT
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        image_data = request.data.get('image', None)
        if not image_data:
            return Response({"detail": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        # 1) Decodificar base64 -> bytes
        try:
            img_bytes = base64.b64decode(image_data)
        except Exception:
            return Response({"detail": "Error decoding base64"}, status=status.HTTP_400_BAD_REQUEST)

        # 2) Convertir a np array (OpenCV)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_cv2 is None:
            return Response({"detail": "Invalid image"}, status=status.HTTP_400_BAD_REQUEST)

        # 3) Extraer encoding
        rgb_img = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_img)
        if not encodings:
            return Response({"detail": "No face detected"}, status=status.HTTP_400_BAD_REQUEST)
        encoding = encodings[0]

        # 4) Convertir encoding a string para almacenarlo
        encoding_str = ' '.join(map(str, encoding.tolist()))

        # 5) Guardar la imagen en profile_image (Django Files)
        file_obj = ContentFile(img_bytes, name='profile_image.jpg')

        user = request.user
        user.face_encoding = encoding_str
        # user.profile_image.save(<filename>, <file>, save=False) si quieres un nombre distinto:
        user.profile_image.save('profile_image.jpg', file_obj, save=False)

        user.save()
        return Response({"detail": "Face encoding and image updated"}, status=status.HTTP_200_OK)

class FacialLoginView(APIView):
    """
    Recibe una imagen base64, genera encoding y compara con la BD.
    Si coincide con algún usuario, retorna tokens JWT.
    """
    def post(self, request):
        image_data = request.data.get('image', None)
        if not image_data:
            return Response({"detail": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        # 1) Decodificar base64
        try:
            img_bytes = base64.b64decode(image_data)
        except Exception:
            return Response({"detail": "Error decoding base64"}, status=status.HTTP_400_BAD_REQUEST)

        nparr = np.frombuffer(img_bytes, np.uint8)
        img_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_cv2 is None:
            return Response({"detail": "Invalid image"}, status=status.HTTP_400_BAD_REQUEST)

        # 2) Extraer encoding
        rgb_img = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_img)
        if not encodings:
            return Response({"detail": "No face detected"}, status=status.HTTP_400_BAD_REQUEST)

        current_encoding = encodings[0]

        # 3) Comparar con usuarios en la BD
        users = User.objects.exclude(face_encoding__isnull=True).exclude(face_encoding='')
        for user in users:
            user_vector = np.fromstring(user.face_encoding, sep=' ')
            match = face_recognition.compare_faces([user_vector], current_encoding, tolerance=0.6)
            if match[0]:
                # 4) Generar JWT si coincide
                refresh = RefreshToken.for_user(user)
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user_id": user.id,
                    "email": user.email,
                    "username": user.username
                }, status=status.HTTP_200_OK)

        return Response({"detail": "No match found"}, status=status.HTTP_401_UNAUTHORIZED)
