from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterView, UpdateFaceAndImageView, FacialLoginView, UserListView, UserDetailView
from .serializers import EmailTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('update_face/', UpdateFaceAndImageView.as_view(), name='update_face'),
    path('facial_login/', FacialLoginView.as_view(), name='facial_login'),

    # Rutas de JWT para login (usuario/contraseña)
    # Si deseas login con 'email' en vez de 'username', define un TokenView personalizado:
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # refresh token
        # Listar y detalle de usuarios (CRUD)
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),


]
