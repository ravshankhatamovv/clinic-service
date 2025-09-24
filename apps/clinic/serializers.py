from rest_framework import serializers
from .models import Doctor, Patient, Appointment, Note, Announcement, VisitorAppointment

class VisitorAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitorAppointment
        fields = "__all__"
        read_only_fields = ["visitor_id", "status", "created_at"]

    def create(self, validated_data):
        validated_data["visitor_id"] = self.context["request"].user.id
        return super().create(validated_data)


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = "__all__"

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"
        extra_kwargs = {
            "doctor": {"read_only": True}
        }

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = "__all__"

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"
        read_only_fields = ("created_by_user_id", "created_by_role", "created_at")

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = "__all__"
        read_only_fields = ("created_by_user_id", "created_at")
