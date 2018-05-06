"""
data序列化
"""
from utils.functions import log
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'

        
class RegisterSerializer(serializers.ModelSerializer):

    username = serializers.EmailField()
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ['username', 'password']

    def validate_username(self, value):
        """
        检查用户名是否唯一
        """
        user = User.objects.filter(username=value)
        if user:
            raise serializers.ValidationError("该邮箱已被注册")
        return value

    def create(self, validated_data):
        validated_data["email"] = validated_data.get('username')
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username_validator = UnicodeUsernameValidator()

    username = serializers.CharField(
        max_length=150,
        validators=[username_validator],
    )
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )


class SendResetMailSerializer(serializers.Serializer):
    username_validator = UnicodeUsernameValidator()

    username = serializers.CharField(
        max_length=150,
        validators=[username_validator],
    )

    def validate_username(self, value):
        """
        检查用户名是否存在
        """
        user = User.objects.filter(username=value)
        if not user:
            raise serializers.ValidationError("该账号尚未注册")
        return value


class PasswordResetSerializer(serializers.Serializer):

    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    def get_user_from_token(self, token):
        token_data = User.decode_token(token)
        uid = token_data.get('id')
        try:
            user = User.objects.get(id=uid)
        except Exception:
            user = None
        return user

    def update(self, instance, validated_data):
        password = validated_data.get('password')
        instance.set_password(password)
        instance.save()
        return instance


class PasswordChangeSerializer(serializers.Serializer):

    old_password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )
    new_password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    def check(self, instance, validated_data):
        old_password = validated_data.get('old_password')
        if not instance.check_password(old_password):
            return False
        return True

    def update(self, instance, validated_data):
        new_password = validated_data.get('new_password')
        instance.set_password(new_password)
        instance.save()
        return instance
