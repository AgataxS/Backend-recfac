from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterView, UpdateFaceAndImageView, FacialLoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('update_face/', UpdateFaceAndImageView.as_view(), name='update_face'),
    path('facial_login/', FacialLoginView.as_view(), name='facial_login'),

    # Rutas de JWT (opcional: login tradicional con user/pass)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
