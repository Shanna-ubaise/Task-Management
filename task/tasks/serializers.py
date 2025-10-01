from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task, Profile

class TaskSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    assigned_to_username = serializers.ReadOnlyField(source='assigned_to.username')

    class Meta:
        model = Task
        fields = '__all__'

class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

    def validate(self, data):
        if data.get('status') == 'Completed':
            if not data.get('completion_report'):
                raise serializers.ValidationError("Completion report is required when marking completed.")
            if not data.get('worked_hours'):
                raise serializers.ValidationError("Worked hours are required when marking completed.")
        return data


class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Profile.ROLE_CHOICES, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        role = validated_data.pop('role')
        password = validated_data.pop('password')
        user = User.objects.create(username=validated_data['username'], is_active=True)
        user.set_password(password)
        user.save()
        Profile.objects.create(user=user, role=role)
        return user
