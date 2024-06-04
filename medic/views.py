from rest_framework import generics, permissions
from .models import Medic, SocialAuthData, Review, Booking
from .serializers import MedicSerializer, SocialAuthDataSerializer, ReviewSerializer, BookingSerializer
from .models import CustomUser
from .utils import calculate_distance
from rest_framework import status
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .sms_client import send_sms
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class MedicListCreateAPIView(generics.ListCreateAPIView):
    queryset = Medic.objects.all()
    serializer_class = MedicSerializer

    def get_queryset(self):
        queryset = Medic.objects.all()
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')
        search_query = self.request.query_params.get('search')
        
        # Check if lat and lon are provided
        if lat is not None and lon is not None:
            # Convert lat and lon to float
            lat = float(lat)
            lon = float(lon)
    
            # Filter nurses based on coverage radius
            queryset = [
                nurse for nurse in queryset
                if calculate_distance(lat, lon, nurse.location.latitude, nurse.location.longitude) <= nurse.area_coverage_km
            ]
        elif search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(expertise__name__icontains=search_query)
            ).distinct()
        else:
            # If lat and lon are not provided, return an empty queryset
            queryset = queryset.none()

        return queryset
    
    def perform_create(self, serializer):
        # Handle additional logic during Medic creation if necessary
        serializer.save()

    def create(self, request, *args, **kwargs):
        # Create a new Medic instance
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
     
class MedicRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Medic.objects.all()
    serializer_class = MedicSerializer

class SocialAuthDataListCreateAPIView(generics.ListCreateAPIView):
    queryset = SocialAuthData.objects.all()
    serializer_class = SocialAuthDataSerializer
    permission_classes = [permissions.AllowAny]  # Adjust permissions as needed

    def perform_create(self, serializer):
        email = serializer.validated_data.get('email')
        full_name = serializer.validated_data.get('name', '')

        # Split the full name into first and last names
        name_parts = full_name.split()
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        user = CustomUser.objects.filter(email=email).first()
        if not user:
            # If the user doesn't exist, create a new one
            user = CustomUser.objects.create_user(email=email, first_name=first_name, last_name=last_name)

        # Check if SocialAuthData for this provider and UID already exists
        provider = serializer.validated_data.get('provider')
        uid = serializer.validated_data.get('social_user_id')
        social_auth_instance = SocialAuthData.objects.filter(user=user, provider=provider, social_user_id=uid).first()

        if social_auth_instance:
            # If it exists, update it
            serializer.update(social_auth_instance, serializer.validated_data)
        else:
            # If it doesn't exist, create a new one
            serializer.save(user=user)
            
        login(self.request, user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = self.request.user
        medic = Medic.objects.filter(user=user).first()
        if medic:
            medic_data = MedicSerializer(medic).data
            response.data['medic'] = medic_data
        return response

class ReviewListCreateAPIView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(status='active')
    
@api_view(['POST'])
def send_sms_api(request):
    if request.method == 'POST':
        phone_number = request.data.get('phone_number')
        message = request.data.get('message')

        if not phone_number or not message:
            return Response({'error': 'phone_number and message are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Call the send_sms function
            send_sms(phone_number, message)
            return Response({'success': 'SMS sent successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def update_availabilty(request):
    if request.method == 'POST':
        medic_id = request.data.get('medic_id')
        available = request.data.get('available')
        email = request.data.get('email')

        if not medic_id or available is None or email is None:
            return Response({'error': 'medic_id, email and available are required'}, status=status.HTTP_400_BAD_REQUEST)

        medic = Medic.objects.filter(id=medic_id, email=email).first()
        if not medic:
            return Response({'error': 'Medic not found'}, status=status.HTTP_404_NOT_FOUND)

        medic.available = available
        medic.save()

        return Response({'success': 'Availability updated successfully'}, status=status.HTTP_200_OK)
    
from django.contrib.auth import logout

@api_view(['POST'])
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return Response({'success': 'Logged out successfully'}, status=status.HTTP_200_OK)
    
import random

def generate_otp():
    return str(random.randint(1000, 9999))

class BookingListAPIView(generics.ListAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

class BookingRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

class RecentPatientBookingView(generics.GenericAPIView):
    serializer_class = BookingSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        bookings = Booking.objects.filter(patient__email=email, status__in=['initiated', 'location_shared', 'in_progress', 'confirmed'])

        if bookings.count() > 1:
            most_recent_booking = bookings.order_by('-created_at').first()
            bookings.exclude(id=most_recent_booking.id).update(status='cancelled')
        else:
            most_recent_booking = bookings.first()

        if most_recent_booking:
            serializer = self.get_serializer(most_recent_booking)
            return Response(serializer.data)
        else:
            return Response({'error': 'No active bookings found'}, status=status.HTTP_404_NOT_FOUND)

class RecentNurseBookingView(generics.GenericAPIView):
    serializer_class = BookingSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        bookings = Booking.objects.filter(medic__user__email=email, status__in=['initiated', 'location_shared', 'in_progress', 'confirmed'])

        if bookings.count() > 1:
            most_recent_booking = bookings.order_by('-created_at').first()
            bookings.exclude(id=most_recent_booking.id).update(status='cancelled')
        else:
            most_recent_booking = bookings.first()

        if most_recent_booking:
            serializer = self.get_serializer(most_recent_booking)
            return Response(serializer.data)
        else:
            return Response({'error': 'No active bookings found'}, status=status.HTTP_404_NOT_FOUND)

class InitiateBookingView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        medic_id = request.data.get('medic_id')
        patient_email = request.data.get('patient_email')  # Assuming patient_id is passed in the request
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
        medic_profile = get_object_or_404(Medic, id=medic_id)
        patient_profile = get_object_or_404(CustomUser, email=patient_email)

        # Check if the nurse is available
        if not medic_profile.available:
            return Response({'error': 'Medic is not available for booking.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the booking
        booking = Booking(
            patient=patient_profile,
            medic=medic_profile,
            status='initiated',
            latitude=latitude,
            longitude=longitude
        )
        booking.save()

        # Set nurse as unavailable
        medic_profile.available = False
        medic_profile.save()

        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UpdateBookingView(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def update(self, request, *args, **kwargs):
        booking = self.get_object()

        if booking.status != 'initiated':
            return Response({'error': 'Invalid booking status.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            otp = generate_otp()
            booking.otp = otp
            booking.status = 'location_shared'
            booking.medic.available = False
            booking.medic.save()
            booking.save()

        # Send WebSocket message to notify nurse
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'booking_{booking.id}',
                {
                    'type': 'booking_update',
                    'message': 'Location shared by patient'
                }
            )

            # Send OTP to patient's phone number
            send_sms(booking.medic.phone_number, f"Your booking has been confirmed, Please use this OTP {otp} once the provider arrives. Thank You! Nursera Team.")
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConfirmBookingView(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        otp = request.data.get('otp')

        # Verify OTP
        if booking.otp != str(otp):
            return Response({'error': 'OTP is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update booking status and make nurse available again
        booking.status = 'confirmed'
        booking.medic.available = True
        booking.medic.save()
        booking.save()
        
        # Send WebSocket message to patient
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
                f'booking_{booking.id}',
                {
                    'type': 'booking_update',
                    'message': 'Booking confirmed and completed.'
                }
            )

        return Response({'status': 'Booking confirmed.'})

class CompleteBookingView(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def update(self, request, *args, **kwargs):
        booking = self.get_object()

        # Update booking status and make nurse available again
        booking.status = 'completed'
        booking.medic.available = True
        booking.medic.save()
        booking.save()
       
        return Response({'status': 'Booking confirmed and completed.'})

class CancelBookingView(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        booking.status = 'cancelled'
        booking.medic.available = True
        booking.medic.save()
        booking.save()

        return Response({'status': 'Booking cancelled.'})