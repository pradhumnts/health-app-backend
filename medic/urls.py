from django.urls import path
from .views import MedicListCreateAPIView, MedicRetrieveUpdateDestroyAPIView, send_sms_api,  SocialAuthDataListCreateAPIView, ReviewListCreateAPIView, update_availabilty, logout_view, InitiateBookingView, ConfirmBookingView, CancelBookingView, UpdateBookingView, BookingListAPIView, BookingRetrieveAPIView, RecentPatientBookingView, RecentNurseBookingView, CompleteBookingView

# If you're using generic views
urlpatterns = [
    path('medics/', MedicListCreateAPIView.as_view(), name='medic-list-create'),
    path('medics/<int:pk>/', MedicRetrieveUpdateDestroyAPIView.as_view(), name='medic-retrieve-update-destroy'),
    path('social-auth-data/', SocialAuthDataListCreateAPIView.as_view(), name='social-user-create'),
    path('reviews/', ReviewListCreateAPIView.as_view(), name='review-list-create'),
    path('send-sms/', send_sms_api, name='send-sms'),
    path('medic/update-availability/', update_availabilty, name='update-availability'),
    path('logout_view', logout_view, name='logout_view'),
    path('bookings/', BookingListAPIView.as_view(), name="booking-list"),
    path('bookings/<int:pk>/', BookingRetrieveAPIView.as_view(), name="booking-list"),
    path('booking/initiate/', InitiateBookingView.as_view(), name='booking-retrieve'),
    path('booking/<int:pk>/update/', UpdateBookingView.as_view(), name='update-booking'),
    path('booking/<int:pk>/confirm/', ConfirmBookingView.as_view(), name='confirm-booking'),
    path('booking/<int:pk>/complete/', CompleteBookingView.as_view(), name='complete-booking'),
    path('booking/<int:pk>/cancel/', CancelBookingView.as_view(), name='cancel-booking'),
    path('bookings/recent/patient/', RecentPatientBookingView.as_view(), name='recent-patient-booking'),
    path('bookings/recent/nurse/', RecentNurseBookingView.as_view(), name='recent-nurse-booking'),
]