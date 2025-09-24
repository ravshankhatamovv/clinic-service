from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorViewSet, PatientViewSet, AppointmentViewSet, NoteViewSet, AnnouncementViewSet, VisitorAppointmentViewSet

router = DefaultRouter()
router.register(r"doctors", DoctorViewSet, basename="doctors")
router.register(r"patients", PatientViewSet, basename="patients")
router.register(r"appointments", AppointmentViewSet, basename="appointments")
router.register(r"notes", NoteViewSet, basename="notes")
router.register(r"announcements", AnnouncementViewSet, basename="announcements")
router.register(r"visitor-appointments", VisitorAppointmentViewSet, basename="visitorappointment")

urlpatterns = [
    path("", include(router.urls))

]
