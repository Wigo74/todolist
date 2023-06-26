from rest_framework.exceptions import NotAuthenticated, ValidationError, AuthenticationFailed
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password

USER_MODEL = get_user_model()


class PasswordFields(serializers.CharField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        kwargs['style'] = {'input_type': 'password'}
        kwargs.setdefault('write_only', True)
        self.validators.append(validate_password)


class RegistrationSerializer(serializers.ModelSerializer):
    password = PasswordFields()
    password_repeat = PasswordFields()

    class Meta:
        read_only_fields = ("id",)
        model = USER_MODEL
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'password_repeat')

    def validate(self, attrs: dict):
        if attrs["password"] != attrs["password_repeat"]:
            raise ValidationError("password and password_repeat is not equal")
        return attrs

    def create(self, validated_data):
        del validated_data['password_repeat']
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class LoginSerializer(serializers.ModelSerializer):
    """ Авторизация пользователя на сайте"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs: dict):
        if not (user := authenticate(
                username=attrs['username'],
                password=attrs['password']
        )):
            raise AuthenticationFailed
        return user

    # class Meta:
    #     read_only_fields = ("id",)
    #     model = USER_MODEL
    #     fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'password_repeat')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = USER_MODEL
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class UpdatePasswordSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if not (user := attrs['user']):
            raise NotAuthenticated
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({'old_password': 'incorrect password'})
        return attrs

    # def create(self, validated_data):
    #     raise NotImplementedError

    def update(self, instance, validated_data):
        instance.password = make_password(validated_data['new_password'])
        instance.save(update_fields=('password',))
        return instance

    class Meta:
        model = USER_MODEL
        read_only_fields = ("id",)
        fields = ('user', 'old_password', 'new_password')
