from rest_framework import serializers
from .models import Trip, UserProfile
from django.contrib.auth.models import User


class TripSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


# class UserProfileSerializer(serializers.ModelSerializer):
#     user = UserSerializer()
#
#     class Meta:
#         model = UserProfile
#         fields = '__all__'
# class UserProfileSerializer(serializers.ModelSerializer):
#     user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
#
#     class Meta:
#         model = UserProfile
#         fields = '__all__'
#         read_only_fields = ['user_id']
#
#     def create(self, validated_data):
#         validated_data['user_id'] = self.context['request'].user
#         return super().create(validated_data)
#
#     def update(self, instance, validated_data):
#         # Сохраняем обновления в экземпляре профиля пользователя
#         validated_data.pop('user_id', None)
#         instance.name = validated_data.get('name', instance.name)
#         instance.phone = validated_data.get('phone', instance.phone)
#         instance.avatar = validated_data.get('avatar', instance.avatar)
#         instance.about = validated_data.get('about', instance.about)
#         instance.save()
#
#         return instance

# class UserProfileSerializer(serializers.ModelSerializer):
#     user_id = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
#
#     class Meta:
#         model = UserProfile
#         fields = '__all__'
#         read_only_fields = ['user_id']
#
#     def create(self, validated_data):
#         # user = self.context['request'].user
#         validated_data['user_id'] = self.context['request'].user
#         return super().create(validated_data)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


