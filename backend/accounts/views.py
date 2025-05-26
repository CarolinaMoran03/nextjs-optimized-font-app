from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Profile
from .serializers import UserSerializer, ProfileSerializer, RegisterSerializer, LoginSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        user.profile.role = 'docente'  # Set default role as docente
        user.profile.save()

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)
        
        if user:
            login(request, user)
            return Response({
                'user': UserSerializer(user).data,
                'profile': ProfileSerializer(user.profile).data
            })
        return Response(
            {'error': 'Credenciales inválidas'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'message': 'Sesión cerrada exitosamente'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    return Response({
        'user': UserSerializer(request.user).data,
        'profile': ProfileSerializer(request.user.profile).data
    })

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_default_admin(request):
    if not request.user.is_superuser:
        return Response(
            {'error': 'No autorizado'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if User.objects.filter(username='admin').exists():
        return Response(
            {'message': 'El usuario admin ya existe'},
            status=status.HTTP_400_BAD_REQUEST
        )

    admin_user = User.objects.create_superuser(
        username='admin',
        password='admin',
        email='admin@example.com'
    )
    admin_user.profile.role = 'admin'
    admin_user.profile.save()

    return Response({
        'message': 'Usuario admin creado exitosamente',
        'user': UserSerializer(admin_user).data
    })
