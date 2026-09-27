from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Report
from .serializers import ReportCreateSerializer

class ReportCreateView(generics.CreateAPIView):
    """
    POST /api/reports/
    
    Create a new report against a user.
    """
    queryset = Report.objects.all()
    serializer_class = ReportCreateSerializer
    permission_classes = [IsAuthenticated]
