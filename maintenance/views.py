from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from users.permissions import IsAdmin
from .models import MaintenanceStatus
from .serializers import MaintenanceStatusSerializer
from .utils import api_response


def _to_bool(value):
    """Coerce JSON bool or string 'true'/'false' to Python bool."""
    if isinstance(value, bool):
        return value
    return str(value).lower() in ('true', '1', 'yes')


def _latest():
    """Always return the most recently created record, or None."""
    return MaintenanceStatus.objects.order_by('-created_at').first()


def _record_data(record):
    return {
        'id': record.id,
        'status': record.status,
        'reason': record.reason or '',
        'created_at': record.created_at,
    }


# ── Public status check ───────────────────────────────────────────────────────

class MaintenanceStatusAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            record = _latest()
            if not record:
                record = MaintenanceStatus.objects.create(status=False, reason='')
            return api_response(
                True, 'Maintenance status retrieved successfully.',
                _record_data(record), status.HTTP_200_OK, status.HTTP_200_OK
            )
        except Exception as e:
            return api_response(False, str(e), None,
                                status.HTTP_500_INTERNAL_SERVER_ERROR,
                                status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Admin — create ────────────────────────────────────────────────────────────

class CreateMaintenanceStatusAPIView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        try:
            raw_status = request.data.get('status')
            if raw_status is None:
                return api_response(False, 'status field is required.', None,
                                    status.HTTP_400_BAD_REQUEST,
                                    status.HTTP_400_BAD_REQUEST)

            record = MaintenanceStatus.objects.create(
                status=_to_bool(raw_status),
                reason=request.data.get('reason', ''),
            )
            return api_response(
                True, 'Maintenance status created successfully.',
                _record_data(record), status.HTTP_201_CREATED, status.HTTP_201_CREATED
            )
        except Exception as e:
            return api_response(False, str(e), None,
                                status.HTTP_500_INTERNAL_SERVER_ERROR,
                                status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Admin — update ────────────────────────────────────────────────────────────

class UpdateMaintenanceStatusAPIView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        try:
            record = _latest()
            if not record:
                record = MaintenanceStatus.objects.create(status=False, reason='')

            if 'status' in request.data:
                record.status = _to_bool(request.data['status'])
            if 'reason' in request.data:
                record.reason = request.data['reason']
            record.save()

            return api_response(
                True, f'Maintenance status updated to {record.status}.',
                _record_data(record), status.HTTP_200_OK, status.HTTP_200_OK
            )
        except Exception as e:
            return api_response(False, str(e), None,
                                status.HTTP_500_INTERNAL_SERVER_ERROR,
                                status.HTTP_500_INTERNAL_SERVER_ERROR)
