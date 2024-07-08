from rest_framework.serializers import ModelSerializer
from .models import CustomUser, Organisation
from django.db.utils import IntegrityError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class CustomUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["firstName", "lastName", "email", "password", "phone"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        try:
            user = CustomUser.objects.create(
                firstName=validated_data.get("firstName"),
                lastName=validated_data.get("lastName"),
                email=validated_data.get("email"),
                phone=validated_data.get("phone", ""),
            )

            user.set_password(validated_data["password"])
            user.save()

            return user

        except IntegrityError as e:
            raise serializers.ValidationError(
                f"An error occurred during user creation: Integrity error - {str(e)}"
            )

        except Exception as e:
            raise serializers.ValidationError(
                f"An error occurred during user creation: {str(e)}"
            )

    def validate(self, attrs):
        email_exist = CustomUser.objects.filter(email=attrs.get("email")).exists()
        if email_exist:
            raise serializers.ValidationError("Email already exists")
        return super().validate(attrs)


class OrganizationSerializer(ModelSerializer):
    class Meta:
        model = Organisation
        fields = "__all__"


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["userId"] = user.userId
        token["email"] = user.email
        # ...

        return token
