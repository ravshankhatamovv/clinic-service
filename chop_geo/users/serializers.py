from urllib.parse import quote

import requests
from django.contrib.auth import get_user_model
from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def send_lead_to_crm(data, username):
    full_name = data.get("name")
    car_model = data.get('model_name')
    if full_name and car_model:

        response = requests.post("https://crmapi.leetcode.uz/api/leads/v1/create",
                                 json={"full_name": full_name, "phone_number": username, "car_model": car_model}
                                 )
        if response.status_code in (200, 201):
            return response.json()['id'], None
        return None, response.text


def get_driver_or_lead_uuid(username):
    # Replace with your dynamic phone number
    encoded_phone_number = quote(username)  # URL-encode the phone number (e.g., + becomes %2B)
    url = f"https://crmapi.leetcode.uz/api/driver/v1/me/{encoded_phone_number}/"

    headers = {
        "accept": "application/json"
    }

    response = requests.get(url, headers=headers)

    # Check response
    if response.status_code == 200:
        try:
            data = response.json()
            driver_uuid = data.get("driver_uuid")
            lead_uuid = data.get("lead_uuid")
            if driver_uuid:
                user = User.objects.get(username=username)
                if user.driver_guid != driver_uuid:  # Проверяем, изменилось ли значение
                    user.driver_guid = driver_uuid
                    user.save()
            return {'driver_uuid': driver_uuid, 'lead_uuid': lead_uuid}
        except ValueError:
            return None
    else:
        print(f"Failed to retrieve data: {response.status_code}")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'guid', 'driver_guid', 'status', 'username']

    def to_representation(self, instance):
        # Get the default representation
        representation = super().to_representation(instance)

        # Customizing the representation
        representation['me_uuid'] = get_driver_or_lead_uuid(username=instance.username)
        return representation


class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    name = serializers.CharField(required=False)
    model_name = serializers.CharField(required=False)

    def create(self, validated_data):
        username = validated_data.get("username")
        name = validated_data.get("name")
        model_name = validated_data.get("model_name")
        data = {}
        if model_name:
            data["model_name"] = model_name
        if name:
            data["name"] = name
        if model_name and name:
            guid, message = send_lead_to_crm(data, username)
            if guid is None:
                raise ValidationError({"subject": "Не работает система", "message": message})
            data['guid'] = guid
        user, _updated = get_user_model().objects.update_or_create(
            username=username, defaults=data)
        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    newpassword = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        exclude = ["is_staff", "groups", "user_permissions", "password"]
        extra_kwargs = {
            'last_login': {'read_only': True},
            'date_joined': {'read_only': True},
            'is_superuser': {'read_only': True},
            'picture': {'read_only': True}
        }

    def update(self, instance, validated_data):
        new_password = validated_data.pop('newpassword', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if new_password:
            instance.set_password(new_password)
        instance.save()
        return instance


class UserMeSerializer(serializers.Serializer):
    user = UserSerializer(many=False)


class TokenObtainSerializer(serializers.Serializer):
    # For register
    username = serializers.CharField()
    otp_code = serializers.CharField(max_length=6)
    model_name = serializers.CharField()
    name = serializers.CharField()

    default_error_messages = {
        "no_active_account": "No active account found with the given credentials"
    }

    token_class = RefreshToken

    def validate(self, attrs):
        username = attrs.get("username")
        name = attrs.get("name")
        model_name = attrs.get("model_name")
        otp_code = attrs.get('otp_code')
        data = {}
        if model_name:
            data["model_name"] = model_name
        if name:
            data["name"] = name
        if model_name and name:
            guid, message = send_lead_to_crm(data, username)
            if guid is None:
                raise ValidationError({"subject": "Не работает система", "message": message})
            data['guid'] = guid
        user, _created = get_user_model().objects.update_or_create(
            username=username, defaults=data if data else None)

        # Validate OTP code
        # try:
        #     otp_record = OTPCode.objects.get(user=user, code=otp_code)
        # except OTPCode.DoesNotExist:
        #     raise exceptions.AuthenticationFailed(
        #         self.error_messages["invalid_otp"],
        #         "invalid_otp",
        #     )

        if otp_code != "1234":
            raise exceptions.AuthenticationFailed(
                {"invalid_otp": "invalid_otp", }
            )
        driver_or_lead_uuid = get_driver_or_lead_uuid(username=username)
        self.user = user
        refresh = self.get_token(self.user)
        data = {}
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        data["data"] = driver_or_lead_uuid

        return data

    @classmethod
    def get_token(cls, user):
        return cls.token_class.for_user(user)  # type: ignore
