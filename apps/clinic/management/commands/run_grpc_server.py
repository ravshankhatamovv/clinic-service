# apps/core/management/commands/run_grpc_server.py
from django.core.management.base import BaseCommand
import grpc
from concurrent import futures
from apps.clinic.generated import clinic_pb2, clinic_pb2_grpc
from apps.clinic.grpc_server import ClinicServiceServicer

class Command(BaseCommand):
    help = "Run gRPC server"

    def handle(self, *args, **options):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        clinic_pb2_grpc.add_ClinicServiceServicer_to_server(ClinicServiceServicer(), server)
        server.add_insecure_port("[::]:50051")
        self.stdout.write(self.style.SUCCESS("gRPC server running on port 50051..."))
        server.start()
        server.wait_for_termination()
