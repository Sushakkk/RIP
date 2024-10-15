from rest_framework import serializers

from .models import *


class SelfEmployedSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    moderator_username = serializers.CharField(source='moderator.username', read_only=True)
    class Meta:
        model = SelfEmployed
        fields = ['id', 'user_username', 'fio', 'created_date', 'modification_date', 'completion_date', 'moderator_username', 'status']

    def get_user_username(self, obj):
        return obj.user.username  # Возвращаем username вместо user_id


class ActivitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activities
        fields = '__all__'



class SelfEmployedActivitiesSerializer(serializers.ModelSerializer):
    self_employed = SelfEmployedSerializer(read_only=True)
    activities = ActivitiesSerializer(read_only=True)

    class Meta:
        model = SelfEmployedActivities
        fields = '__all__'

 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email','first_name', 'last_name', 'username')


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email','first_name', 'last_name', 'username', 'password', )
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)




