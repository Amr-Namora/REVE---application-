from django.urls import path
from . import views

urlpatterns = [
    path('', views.intro, name='intro'),
    path('notifications/', views.get_notifications, name='get_notifications'),
    path('gallery/', views.gallery, name='gallery'),
    path('review/<str:pk>/', views.create_review, name='review'),
    path('gallery/<str:pk>/', views.res_profile, name='res_profile'),
    path('comments_of_realestate/<str:pk>/', views.comments_of_realestate, name='comments_of_realestate'),
    path('new_realestate/', views.new_realestate, name='new_realestate'),
    path('favourit/', views.favourit_view, name='favourit'),
    path('profile/', views.profile, name='profile'),
    path('reservation/<int:realestate_id>/', views.create_reservation_period, name='create-reservation'),
    path('DaysOff/<int:realestate_id>/', views.create_DaysOff_period, name='create-DaysOff'),
    path('toggle-favorite/<int:realestate_id>/', views.toggle_favorite, name='toggle-favorite'),
    path('property_bookings/<int:realestate_id>/', views.property_bookings, name='property-bookings'),
    path('get_accepted_reservations/<int:realestate_id>/', views.get_accepted_reservations, name='get_accepted_reservations'),
    # New endpoints for notifications/actions:
    # path('reservation/assign/<int:reservation_id>/', views.assign_reservation, name='assign_reservation'),
    # path('reservation/handle/<int:reservation_id>/', views.handle_assignment_action, name='handle_assignment_action'),
    path('notifications/assign-realestate/', views.assign_realestate_notification,
         name='assign_realestate_notification'),
    path('reservation/assign/', views.assign_reservation_notification, name='assign_reservation_notification'),
    path('reservation/response/', views.handle_reservation_response, name='handle_reservation_response'),
    path('api/save-token/', views.save_expo_push_token, name='save-token'),
    path('api/send-notification/', views.send_push_notification_view, name='send-notification'),
    path('phones_admins/', views.admins_phones, name='phones_admins'),

]
