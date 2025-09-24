from django.db import models

class Doctor(models.Model):
    # store auth-service user id
    user_id = models.IntegerField(unique=True, db_index=True)
    full_name= models.CharField(max_length=255, null=True, blank=True)
    specialization= models.CharField(max_length=255, null=True, blank=True)
    clinic_name= models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Doctor(user_id={self.user_id})"

class Patient(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="patients")
    nurse_id = models.IntegerField(null=True, blank=True, db_index=True)  
    first_name=models.CharField(max_length=255, null=True, blank=True)
    last_name=models.CharField(max_length=255, null=True, blank=True)
    age=models.IntegerField(null=True, blank=True)
    


    def __str__(self):
        return f"Patient(user_id={self.user_id})"

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments")
    time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("doctor", "time") 
        
    def __str__(self):
        return f"Appt {self.id} at {self.time.isoformat()}"
from django.db import models

class TreatmentService(models.TextChoices):
    GENERAL_MEDICINE = "general_medicine", "General Medicine"
    PEDIATRICS = "pediatrics", "Pediatrics"
    CARDIOLOGY = "cardiology", "Cardiology"
    NEUROLOGY = "neurology", "Neurology"
    ORTHOPEDICS = "orthopedics", "Orthopedics"
    DERMATOLOGY = "dermatology", "Dermatology"
    GYNECOLOGY = "gynecology", "Gynecology"
    OPHTHALMOLOGY = "ophthalmology", "Ophthalmology"
    DENTISTRY = "dentistry", "Dentistry"
    PSYCHIATRY = "psychiatry", "Psychiatry"

class StatusAppointment(models.TextChoices):
    ACCEPTED="accepted", "Accepted"
    REJECTED="rejeceted", "Rejected"
    IN_PROCESS="in_process", "In_process"

class VisitorAppointment(models.Model):
    visitor_id=models.IntegerField(null=True, blank=True)
    comment=models.TextField(max_length=400, null=True, blank=True)
    treatment_service=models.CharField(choices=TreatmentService.choices, null=True, blank=True)
    time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status=models.CharField(StatusAppointment.choices, default=StatusAppointment.IN_PROCESS, null=True, blank=True)

        
    def __str__(self):
        return f"Appt {self.id} at {self.time.isoformat()}"
class Note(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="notes")
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    created_by_user_id = models.IntegerField()  # auth user id (doctor or nurse)
    created_by_role = models.CharField(max_length=20)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_by_user_id = models.IntegerField()  # moderator id
    created_at = models.DateTimeField(auto_now_add=True)
