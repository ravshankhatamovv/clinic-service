import grpc
from concurrent import futures
from apps.clinic.generated import clinic_pb2, clinic_pb2_grpc
from .models import Doctor
from django.db import transaction

class ClinicServiceServicer(clinic_pb2_grpc.ClinicServiceServicer):
    @transaction.atomic
    def CreateDoctor(self, request, context):
        doctor = Doctor.objects.create(
            user_id=request.user_id,
            specialization=request.specialization,
            clinic_name=request.clinic_name,
            full_name=request.full_name

        )
        return clinic_pb2.DoctorResponse(
            id=doctor.id,
            user_id=doctor.user_id,
            specialization=doctor.specialization,
            clinic_name=doctor.clinic_name,
            full_name=request.full_name,
            # message="Doctor created successfully"
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    clinic_pb2_grpc.add_ClinicServiceServicer_to_server(
        ClinicServiceServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()
