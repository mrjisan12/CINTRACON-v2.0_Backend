from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import EventSerializer, EventInterestSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Event, EventInterest
from .utils import api_response


class EventCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EventSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return api_response(
                True, 
                'Event created successfully!', 
                serializer.data, 
                201, 
                status.HTTP_201_CREATED
            )
        
        return api_response(
            False, 
            'Validation error', 
            serializer.errors, 
            400, 
            status.HTTP_400_BAD_REQUEST
        )


class EventListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            page = int(request.data.get('page', 1))
            size = int(request.data.get('size', 10))
            
            # Validate page and size
            if page < 1:
                return api_response(False, 'Page must be greater than 0', None, 400, status.HTTP_400_BAD_REQUEST)
            if size < 1:
                return api_response(False, 'Size must be greater than 0', None, 400, status.HTTP_400_BAD_REQUEST)
            
            events = Event.objects.all().order_by('-created_at')
            total = events.count()
            start = (page - 1) * size
            end = start + size
            
            # Check if page exists
            if start >= total:
                return api_response(True, 'No more events available', [], 200, status.HTTP_200_OK)
            
            paginated = events[start:end]
            serializer = EventSerializer(
                paginated, 
                many=True, 
                context={'request': request}
            )
            
            data = serializer.data
            
            return api_response(
                True, 
                'Events fetched successfully!', 
                data,
                200, 
                status.HTTP_200_OK
            )
            
        except ValueError:
            return api_response(False, 'Invalid page or size parameter', None, 400, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class EventUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
            
            # Check if the logged-in user is the owner of the event
            if event.user != request.user:
                return api_response(
                    False, 
                    'You can only update your own events', 
                    None, 
                    403, 
                    status.HTTP_403_FORBIDDEN
                )
            
            serializer = EventSerializer(
                event, 
                data=request.data, 
                context={'request': request}, 
                partial=True
            )
            
            if serializer.is_valid():
                serializer.save()
                return api_response(
                    True, 
                    'Event updated successfully!', 
                    serializer.data, 
                    200, 
                    status.HTTP_200_OK
                )
            
            return api_response(
                False, 
                'Validation error', 
                serializer.errors, 
                400, 
                status.HTTP_400_BAD_REQUEST
            )
            
        except Event.DoesNotExist:
            return api_response(
                False, 
                'Event not found', 
                None, 
                404, 
                status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return api_response(
                False, 
                f'Server error: {str(e)}', 
                None, 
                500, 
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EventDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
            
            # Check if the logged-in user is the owner of the event
            if event.user != request.user:
                return api_response(
                    False, 
                    'You can only delete your own events', 
                    None, 
                    403, 
                    status.HTTP_403_FORBIDDEN
                )
            
            event.delete()
            
            return api_response(
                True, 
                'Event deleted successfully!', 
                None, 
                200, 
                status.HTTP_200_OK
            )
            
        except Event.DoesNotExist:
            return api_response(
                False, 
                'Event not found', 
                None, 
                404, 
                status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return api_response(
                False, 
                f'Server error: {str(e)}', 
                None, 
                500, 
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EventInterestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
            
            
            # Check if user already interested
            interest_exists = EventInterest.objects.filter(
                user=request.user, 
                event=event
            ).exists()
            
            if interest_exists:
                # Remove interest
                EventInterest.objects.filter(user=request.user, event=event).delete()
                message = 'Interest removed successfully!'
                is_interested = False
            else:
                # Add interest
                EventInterest.objects.create(user=request.user, event=event)
                message = 'Interest added successfully!'
                is_interested = True
            
            # Get updated total interested count
            total_interested = event.total_interested
            
            return api_response(
                True, 
                message, 
                {
                    'is_interested': is_interested,
                    'total_interested': total_interested
                }, 
                200, 
                status.HTTP_200_OK
            )
            
        except Event.DoesNotExist:
            return api_response(
                False, 
                'Event not found', 
                None, 
                404, 
                status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return api_response(
                False, 
                f'Server error: {str(e)}', 
                None, 
                500, 
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

