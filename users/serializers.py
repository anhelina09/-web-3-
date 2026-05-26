from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ['id', 'phone', 'email', 'first_name', 'last_name', 'role', 'is_active', 'password']
        read_only_fields = ['id', 'is_active']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        # Створюємо користувача через наш менеджер, щоб пароль захешувався
        user = CustomUser.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance