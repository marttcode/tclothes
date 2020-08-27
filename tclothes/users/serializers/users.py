"""User's serializer."""

# Django
from django.contrib.auth import authenticate, password_validation
from django.core.validators import RegexValidator

# Django REST framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

# Models
from tclothes.users.models import User, Profile


class UserLoginSerializer(serializers.Serializer):
    """Users login serializer.

    Handle the login request data.
    """

    phone_regex = RegexValidator(
        regex=r'^[0-9]\d{9,14}$',
        message="Numero de telefono debe ser imgresado con el formato: 123456789012. Entre 10 y 15 digitos."
    )
    phone_number = serializers.CharField(
        validators=[phone_regex],
        max_length=15,
        error_messages={
            'max_length': "La longitud maxima de tu numero de telefono debe ser de 15 digitos.",
        }
    )
    password = serializers.CharField(
        min_length=8,
        max_length=64,
        error_messages={
            'min_length': "La longitud minima de la contraseña debe ser de 8 digitos.",
            'max_length': "La longitud maxima de tu contraseña debe ser de 64 digitos.",
            'null': "Este campo no puede ser nulo.",
            'blank': "Este campo no piede ser enviando en blanco."
        }
    )

    def validate(self, attrs):
        """Check credentials."""
        user = authenticate(username=attrs['phone_number'], password=attrs['password'])
        if user is None:
            raise serializers.ValidationError('Credenciales invalidas.')
        self.context['user'] = user
        return attrs

    def create(self, validated_data):
        """Generate or retrieve a new Token."""
        token, created = Token.objects.get_or_create(user=self.context['user'])
        return self.context['user'], token.key


class UserSignUpSerializer(serializers.Serializer):
    """User sign up serializer.
    Handle sign up data validation and user creation.
    """

    # username => phone_number
    username_regex = RegexValidator(
        regex=r'^[0-9]\d{9,14}$',
        message="Numero de telefono debe ser imgresado con el formato: 123456789012. Entre 10 y 15 digitos."
    )
    username_unique = UniqueValidator(queryset=User.objects.all(), message='Este numero, ya se encutra registrado.')
    username = serializers.CharField(
        max_length=15,
        validators=[username_regex, username_unique],
        error_messages={
            'max_length': "La longitud maxima de tu numero de telefono debe ser de 15 digitos.",
        },
    )

    first_name = serializers.CharField(
        max_length=150,
        error_messages={
            'max_length': "La longitud maxima de tu apellido debe ser de 150 digitos.",
        },
    )
    last_name = serializers.CharField(
        max_length=150,
        error_messages={
            'max_length': "La longitud maxima de tu nombre debe ser de 150 digitos.",
        },
    )

    # Password
    password = serializers.CharField(
        min_length=8,
        max_length=64,
        error_messages={
            'min_length': "La longitud minima de la contraseña debe ser de 8 digitos.",
            'max_length': "La longitud maxima de tu contraseña debe ser de 64 digitos.",
            'null': "Este campo no puede ser nulo.",
            'blank': "Este campo no piede ser enviando en blanco."
        },
    )
    password_confirmation = serializers.CharField(
        min_length=8,
        max_length=64,
        error_messages={
            'min_length': "La longitud minima de la contraseña debe ser de 8 digitos.",
            'max_length': "La longitud maxima de tu contraseña debe ser de 64 digitos.",
            'null': "Este campo no puede ser nulo.",
            'blank': "Este campo no piede ser enviando en blanco."
        },
    )

    def validate(self, data):
        """Verify passwords match."""
        password = data['password']
        password_conf = data['password_confirmation']
        if password != password_conf:
            raise serializers.ValidationError("Contraseñas no coinciden.")
        password_validation.validate_password(password)
        return data

    def create(self, data):
        """Handle user and profile creation."""
        data.pop('password_confirmation')
        user = User.objects.create_user(**data)
        Profile.objects.create(user=user)
        return user
