from rest_framework import serializers
from users.models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'confirm_password',
        ]
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False,}
        }

    def validate(self, data):
        pass1 = data.get('password')
        pass2 = data.get('confirm_password')
        if pass1 != pass2:
            raise serializers.ValidationError({
                'confirm_password': 'The password fields must match.'
            })
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        return User.objects.create_user(**validated_data)