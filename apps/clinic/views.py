from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .models import Doctor, Patient, Appointment, Note, Announcement
from .serializers import (
    DoctorSerializer, PatientSerializer, AppointmentSerializer,
    NoteSerializer, AnnouncementSerializer
)
from .permissions import IsAdmin, IsDoctor, IsNurse, IsModerator, IsVisitor
from datetime import datetime, timedelta
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import VisitorAppointment
from .serializers import VisitorAppointmentSerializer
from django.utils import timezone

class VisitorAppointmentViewSet(viewsets.ModelViewSet):
    queryset = VisitorAppointment.objects.all().order_by("-created_at")
    serializer_class = VisitorAppointmentSerializer
    permission_classes = [IsAuthenticated & (IsDoctor | IsNurse | IsVisitor)]

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated & IsAdmin]



class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    queryset = Patient.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", None)

        if role == "doctor":
            
            return Patient.objects.filter(doctor__user_id=user.id)

        elif role == "nurse":
        
            return Patient.objects.filter(nurse_id=user.id)

        return Patient.objects.none()  

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, "role", None) != "doctor":
            raise PermissionDenied("Only doctor can create patient.")

        doctor = Doctor.objects.get(id=user.id)
        serializer.save(doctor=doctor)


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated & (IsDoctor | IsNurse)]


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Logic:
        - If request.user.role == 'nurse' -> nurse can add note for patient assigned to them
        - If 'doctor' -> doctor can add note only for own patient and only if there is an appointment within time window
        """
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        user_role = getattr(request.user, "role", None)
        user_id = getattr(request.user, "id", None)
        patient = request.data.get("patient")
        text = request.data.get("text")
        appointment = request.data.get("appointment", None)

        if not patient or not text:
            return Response({"detail": "patient_id and text required"}, status=400)

        patient = get_object_or_404(Patient, id=patient)

        if user_role == "nurse":
            
            if patient.nurse_user_id != user_id:
                return Response({"detail": "Nurse not assigned to this patient"}, status=403)
            note = Note.objects.create(
                patient=patient,
                appointment=None,
                created_by_user_id=user_id,
                created_by_role="nurse",
                text=text
            )
            return Response(NoteSerializer(note).data, status=201)

        elif user_role == "doctor":
            doctor_entry = Doctor.objects.filter(user_id=user_id).first()
            if not doctor_entry or patient.doctor.id != doctor_entry.id:
                return Response({"detail": "Doctor not owner of this patient"}, status=403)

            if not appointment:
                return Response({"detail": "appointment_id required for doctor notes"}, status=400)

            try:
                appt = Appointment.objects.get(id=appointment)
            except Appointment.DoesNotExist:
                return Response({"detail": "Appointment not found"}, status=404)

            if appt.patient_id != patient.id or appt.doctor_id != doctor_entry.id:
                return Response({"detail": "Appointment mismatch"}, status=403)

            now = timezone.now()  
            window = timedelta(minutes=30)
            if not (appt.time - window <= now <= appt.time + window):
                return Response({"detail": "Can only add doctor note at appointment time"}, status=403)

            note = Note.objects.create(
                patient=patient,
                appointment=appt,
                created_by_user_id=user_id,
                created_by_role="doctor",
                text=text
            )
              
            if patient.nurse_id:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"nurse_{patient.nurse_id}",
                    {
                        "type": "notify",
                        "message": f"Doctor {doctor_entry.full_name} yangi note qo'shdi: {text}",
                        "patient_id": patient.id,
                        "patient_first_name": patient.first_name,
                        "patient_last_name": patient.last_name
                    }
                )

            return Response(NoteSerializer(note).data, status=201)
        else:
            return Response({"detail": "Only nurse or doctor can create notes"}, status=403)
        

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all().order_by("-created_at")
    serializer_class = AnnouncementSerializer

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsAuthenticated & IsModerator]
        else:
            permission_classes = [IsAuthenticated] 
        return [perm() for perm in permission_classes]

    def create(self, request, *args, **kwargs):
        user_id = getattr(request.user, "id", None)
        title = request.data.get("title")
        body = request.data.get("body")

        if not title or not body:
            return Response({"detail": "title and body required"}, status=400)

        ann = Announcement.objects.create(
            title=title,
            body=body,
            created_by_user_id=user_id,
        )
        return Response(AnnouncementSerializer(ann).data, status=201)

