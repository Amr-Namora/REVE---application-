from django.contrib.auth.models import Group
from .filters import RealEstateFilter
from .serializer import Phones_Help_serializer, Custom_Notification_serializer, MYRESERVATIONSerializer, \
    Notifications_group_reservationSerializer, Notifications_group_Serializer, \
    Notifications_group_reservationSerializer, Notifications_Serializer, Notifications_reservationSerializer, \
    ReservationPeriodSerializer, NewRealEstateSerializer, RealEstateSerializer, ReviewSerializer, \
    SecondReviewSerializer, FavouritSerializer
from .models import Phones_Help, Custom_Notification, ReservationRejection, Notifications_group, \
    Notifications_reservation_group, Notifications_reservation, Notifications, ReservationPeriod, RealEstate, Review, \
    NewRealEstate, Second_Review, Favourits
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Avg
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import RealEstate, Favourits
from rest_framework_simplejwt.authentication import JWTAuthentication  # or your respective auth class
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

User = get_user_model()
import requests
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
import random

BAD_WORDS = getattr(settings, "BAD_WORDS",
                    [
                        "طز", "طيز", "خرا",
                        "ass", "bitch", "زب",
                        "كس", "صرماي",
                        "طز", "طيز", "خري",
                        "لعن", "fuck", "dick",
                        "pussy", "حمار", "جحش",
                        "عاهر", "اير"
                    ])


def contains_bad_words(comment):
    """Check if the comment contains any prohibited words."""
    return any(bad_word in comment.lower() for bad_word in BAD_WORDS)


from django.shortcuts import render


def intro(request):
    return render(request, 'intro.html')


# @api_view(['GET'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([AllowAny])
# def gallery(request):
#     user = request.user

#     # Try to get cached queryset
#     cache_key = f"cached_real_estates_{request.GET.urlencode()}"
#     cached_queryset = cache.get(cache_key)

#     if cached_queryset is None:
#         # Apply initial randomization
#         filter_instance = RealEstateFilter(request.GET, queryset=RealEstate.objects.all())
#         randomized_queryset = filter_instance.qs.order_by('?')

#         # Store the full queryset in cache
#         cache.set(cache_key, randomized_queryset, timeout=3600)  # Cache for 1 hour
#     else:
#         # Use cached queryset
#         randomized_queryset = cached_queryset

#     # Apply filtering after retrieving cached queryset
#     filter_instance = RealEstateFilter(request.GET, queryset=randomized_queryset)
#     final_queryset = filter_instance.qs

#     # Recalculate notifications
#     has_unseen = False if isinstance(user, AnonymousUser) else (
#         Notifications_reservation.objects.filter(user_to=user, seen=False).exists() or
#         Notifications.objects.filter(user_to=user, seen=False).exists() or
#         Notifications_group.objects.filter(user_to=user, seen=False).exists() or
#         Notifications_reservation_group.objects.filter(user_to=user, seen=False).exists() or
#         Custom_Notification.objects.filter(user_to=user, seen=False).exists()
#     )

#     serializer = RealEstateSerializer(final_queryset, many=True, context={'request': request})
#     return Response({
#         'real estates': serializer.data,
#         'has_unseen_notifications': int(has_unseen)
#     })


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def gallery(request):
    user = request.user

    # Apply the filter.
    filter_instance = RealEstateFilter(request.GET, queryset=RealEstate.objects.all())
    # Now, order the filtered queryset randomly.
    # real_estate_objects = filter_instance.qs.order_by('?')
    real_estate_objects = filter_instance.qs
    # Recalculate notifications on every request.
    if isinstance(user, AnonymousUser):
        has_unseen = False
    else:
        has_unseen = (
                Notifications_reservation.objects.filter(user_to=user, seen=False).exists() or
                Notifications.objects.filter(user_to=user, seen=False).exists() or
                Notifications_group.objects.filter(user_to=user, seen=False).exists() or
                Custom_Notification.objects.filter(user_to=user, seen=False).exists() or
                Notifications_reservation_group.objects.filter(user_to=user, seen=False).exists()
        )

    serializer = MYRESERVATIONSerializer(
        real_estate_objects,
        many=True,
        context={'request': request}
    )
    return Response({
        'real estates': serializer.data,
        'has_unseen_notifications': int(has_unseen)
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_review(request, pk):
    user = request.user
    real_estate = get_object_or_404(RealEstate, id=pk)
    data = request.data

    # Validate rating
    if not (1 <= data.get("rating", 0) <= 5):
        return Response({"تنبيه": "قيم العقار من نجمة واحدة الى 5 نجوم"}, status=status.HTTP_400_BAD_REQUEST)

    # Validate comment for bad words
    if contains_bad_words(data.get("comment", "")):
        return Response({"تنبيه!": "نرجو منك كتابة تعليق لا يحتوي على كلمات غير محترمة"},
                        status=status.HTTP_400_BAD_REQUEST)

    review = real_estate.review.filter(user=user)

    if review.exists():
        initial_review = review.first()
        Second_Review.objects.create(
            user=user,
            real_estate=real_estate,
            rating=initial_review.rating,
            comment=initial_review.comment,
            createAt=initial_review.createAt
        )
        review.delete()

    # Create new review
    Review.objects.create(
        user=user,
        real_estate=real_estate,
        rating=data["rating"],
        comment=data["comment"]
    )

    # Update the average rating efficiently
    real_estate.ratings = real_estate.review.aggregate(avg_ratings=Avg("rating"))["avg_ratings"]
    real_estate.save()

    return Response({"details": "تم التعليق بنجاح"})


@api_view(['GET'])
def res_profile(request, pk):
    realestate = get_object_or_404(RealEstate, id=pk)
    serializer = RealEstateSerializer(realestate, context={'request': request})
    review = realestate.review
    comments = ReviewSerializer(review, many=True)
    secondreview = realestate.second_review
    secondcomments = SecondReviewSerializer(secondreview, many=True)
    is_reserved = False
    can_view_location = False

    if request.user.is_authenticated:
        today = timezone.now().date()
        # For comments - just check if any accepted reservation exists
        is_reserved = ReservationPeriod.objects.filter(
            realestate=realestate,
            user=request.user,
            status='accepted'
        ).exists()

        # For location - check for active reservation (end_date > today)
        can_view_location = ReservationPeriod.objects.filter(
            realestate=realestate,
            user=request.user,
            status='accepted',
            end_date__gt=today
        ).exists()
    print("hi", is_reserved)
    return Response({
        'is_reserved': is_reserved,
        'can_view_location': can_view_location,
        'realestate': serializer.data,
        'comments': comments.data,
        'secondcomments': secondcomments.data
    })


@api_view(['GET'])
def comments_of_realestate(request, pk):
    realestate = get_object_or_404(RealEstate, id=pk)
    reviews = realestate.review
    serializer = ReviewSerializer(reviews, many=True)
    return Response({'reviews': serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_realestate(request):
    print("1111   ", request.user.username)

    # Check if the user already has a real estate entry
    if NewRealEstate.objects.filter(user=request.user).exists():
        return Response({'details': 'لا يمكنك اضافة عقار اخر حتى يتم اضافة عقارك السابق'},
                        status=status.HTTP_400_BAD_REQUEST)
    print(232)
    data = request.data

    # Validate 'notes' field for bad words
    if contains_bad_words(data.get("notes", "")):
        return Response({"تنبيه!": "نرجو منك عدم كتابة كلمات غير محترمة "},
                        status=status.HTTP_400_BAD_REQUEST)

    if contains_bad_words(data.get("town", "")):
        return Response({"تنبيه!": "نرجو منك عدم كتابة كلمات غير محترمة"},
                        status=status.HTTP_400_BAD_REQUEST)

    serializer = NewRealEstateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)

        # Create a notification for the creator

        try:
            staff_group = Group.objects.get(name="staff")
            # Send notification to every user in the "staff" group.
            staff_users = User.objects.filter(groups=staff_group)
            for staff_member in staff_users:
                print(102)
                Notifications_group.objects.create(
                    client=request.user,
                    user_to=staff_member,
                    notification_type='ready_to_assign_add_realestate_admin',
                )

        except Group.DoesNotExist:
            # If the group is not found, you might log it or choose to do nothing.
            pass
        Notifications.objects.create(
            user_to=request.user,
            notification_type='add_realestate_user',
        )
        return Response({'details': 'تم استلام طلبك بنجاح'}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def favourit_view(request):
    favourites = request.user.favourites
    serializeer = FavouritSerializer(favourites, many=True, context={'request': request})
    return Response({'your favourites': serializeer.data})


from rest_framework.renderers import JSONRenderer
import json

from rest_framework.decorators import api_view, renderer_classes


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def profile(request):
    user = request.user
    person = user.person

    accepted_realestates = ReservationPeriod.objects.filter(status='accepted', user=user).values_list('realestate',
                                                                                                      flat=True)

    accepted_reservations = RealEstate.objects.filter(id__in=accepted_realestates)
    myrealestates = RealEstate.objects.filter(user=user)

    serializer_rel = MYRESERVATIONSerializer(myrealestates, many=True, context={'request': request})
    serializer_res = MYRESERVATIONSerializer(accepted_reservations, many=True, context={'request': request})

    return Response({
        'name': person.name,
        'phone': person.phone,
        'city': person.city,
        'your reservations are': serializer_res.data,
        'your real estates are': serializer_rel.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, realestate_id):
    real_estate = get_object_or_404(RealEstate, id=realestate_id)
    favorite_exists = Favourits.objects.filter(
        user=request.user,
        realestate=real_estate
    ).exists()

    if favorite_exists:
        Favourits.objects.filter(
            user=request.user,
            realestate=real_estate
        ).delete()
        return Response({'is_favorite': False}, status=status.HTTP_200_OK)
    else:
        Favourits.objects.create(
            user=request.user,
            realestate=real_estate
        )
        return Response({'is_favorite': True}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_accepted_reservations(request, realestate_id):
    # Filter for reservations with status accepted or DayOff
    reservations = ReservationPeriod.objects.filter(
        realestate_id=realestate_id,
        status__in=['accepted', 'DayOff', 'pending']
    )
    serializer = ReservationPeriodSerializer(reservations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_DaysOff_period(request, realestate_id):
    print('DaysOff')
    try:
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the reservation period
        reservation = ReservationPeriod.objects.create(
            user=request.user,
            realestate_id=realestate_id,
            start_date=start_date,
            end_date=end_date,
            status='DayOff'
        )
        # Notifications.objects.create(
        #     user_to=request.user,
        #     describtion='لقد تم بنجاح تحديد تاريخ عطلتك و شكرا لك'
        # )
        serializer = ReservationPeriodSerializer(reservation)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def property_bookings(request, realestate_id):
    # Bookings with status "accepted" for current reservations
    accepted_bookings = ReservationPeriod.objects.filter(
        realestate_id=realestate_id, status='accepted'
    )
    # Bookings with status "DayOff" for owner holidays
    dayoff_bookings = ReservationPeriod.objects.filter(
        realestate_id=realestate_id, status='DayOff'
    )

    accepted_serializer = ReservationPeriodSerializer(accepted_bookings, many=True)
    dayoff_serializer = ReservationPeriodSerializer(dayoff_bookings, many=True)

    return Response({
        "accepted_reservations": accepted_serializer.data,
        "dayoff_reservations": dayoff_serializer.data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_reservation_period(request, realestate_id):
    try:
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if ReservationPeriod.objects.filter(user=request.user, status='pending').exists():
            return Response({'تنبيه!': 'لا يمكنك ارسال حجز اخر حتى قبول او رفض حجزك السابق'},
                            status=status.HTTP_400_BAD_REQUEST)
        # Create the reservation period with status pending
        reservation = ReservationPeriod.objects.create(
            user=request.user,
            realestate_id=realestate_id,
            start_date=start_date,
            end_date=end_date,
            status='pending'
        )

        # MyReservations.objects.create(
        #     user=request.user,
        #     realestate_id=realestate_id,
        #     reservationPeriod=reservation
        # )

        # Get the default admin user (ensure a user with username 'admin' exists)

        # Create a notification for the creator
        Notifications_reservation.objects.create(
            user_to=request.user,
            notification_type='still_pending_user',
            reservation=reservation
        )
        Notifications_reservation.objects.create(
            user_to=reservation.realestate.user,
            notification_type='res_pending_to_Owner',
            reservation=reservation
        )

        # Send a notification to every user in the designated group (e.g., "reservation_handlers")
        try:
            staff_group = Group.objects.get(name="staff")
            # Send notification to every user in the "staff" group.
            staff_users = User.objects.filter(groups=staff_group)
            for staff_member in staff_users:
                print(102)
                Notifications_reservation_group.objects.create(
                    client=request.user,
                    user_to=staff_member,
                    notification_type='ready_to_assign_reservation_admin',
                    reservation=reservation
                )
        except Group.DoesNotExist:
            handler_users = []

        # group_message = f"{request.user.username} has asked for a reservation. Would you handle it? (Tap 'assign me')"
        # for user in handler_users:
        #     Notifications_reservation.objects.create(
        #         user_to=user,
        #         describtion=group_message,
        #         notification_type='group_request',
        #         reservation=reservation
        #     )

        serializer = ReservationPeriodSerializer(reservation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def assign_reservation(request, reservation_id):
#     """
#     When a handler clicks the "assign me" button from their notification:
#       - Set the current user as the assigned handler.
#       - Remove all group request notifications for this reservation.
#       - Create a new assignment notification for this handler with the options to accept or reject.
#     """
#     try:
#         reservation = ReservationPeriod.objects.get(id=reservation_id)
#
#         if reservation.assigned_handler:
#             return Response({'error': 'This reservation has already been assigned.'},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         # Ensure that this user belongs to the reservation_handlers group.
#         if not request.user.groups.filter(name='reservation_handlers').exists():
#             return Response({'error': 'You are not authorized to assign this reservation.'},
#                             status=status.HTTP_403_FORBIDDEN)
#
#         admin_user = User.objects.get(username='admin')
#
#         # Set the current user as the handler.
#         reservation.assigned_handler = request.user
#         reservation.save()
#
#         # Remove all group_request notifications for this reservation.
#         Notifications_reservation.objects.filter(
#             reservation=reservation,
#             notification_type='group_request'
#         ).delete()
#
#         # Create a new assignment notification for the handler.
#         Notifications_reservation.objects.create(
#             user_to=request.user,
#             description="The job is yours. Please choose to accept or reject the reservation.",
#             notification_type="assignment",
#             reservation=reservation
#         )
#         return Response({'message': 'Reservation assigned to you.'}, status=status.HTTP_200_OK)
#
#     except ReservationPeriod.DoesNotExist:
#         return Response({'error': 'Reservation not found.'}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def handle_assignment_action(request, reservation_id):
#     """
#     When the assigned handler chooses to accept or reject:
#       - Update the reservation status accordingly.
#       - Remove the assignment notification.
#       - Notify the original reservation creator with the result.
#     Expect a POST parameter "action" with value "accept" or "reject".
#     """
#     try:
#         action = request.data.get("action")
#         if action not in ["accept", "reject"]:
#             return Response({'error': "Action must be 'accept' or 'reject'."},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         reservation = ReservationPeriod.objects.get(id=reservation_id)
#
#         # Verify that the current user is indeed the assigned handler.
#         if reservation.assigned_handler != request.user:
#             return Response({'error': 'You are not assigned to this reservation.'},
#                             status=status.HTTP_403_FORBIDDEN)
#
#         admin_user = User.objects.get(username='admin')
#         if action == "accept":
#             reservation.status = "accepted"
#             result_message = "Your reservation has been accepted."
#         else:  # reject
#             reservation.status = "rejected"
#             result_message = "Your reservation has been rejected."
#
#         reservation.save()
#
#         # Remove the assignment notification that was sent to the handler.
#         Notifications_reservation.objects.filter(
#             reservation=reservation,
#             notification_type="assignment",
#             user_to=request.user
#         ).delete()
#
#         # Notify the creator of the reservation about the result.
#         Notifications_reservation.objects.create(
#             user_to=reservation.user,
#             description=result_message,
#             notification_type="result",
#             reservation=reservation
#         )
#
#         return Response({'message': f"Reservation {action}ed successfully."}, status=status.HTTP_200_OK)
#     except ReservationPeriod.DoesNotExist:
#         return Response({'error': 'Reservation not found.'}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    # Query all notifications for the authenticated user
    notifications_reservation = Notifications_reservation.objects.filter(user_to=request.user)
    notifications = Notifications.objects.filter(user_to=request.user)
    notifications_reservation_group = Notifications_reservation_group.objects.filter(user_to=request.user)
    notifications_group = Notifications_group.objects.filter(user_to=request.user)
    Custom_Notifications = Custom_Notification.objects.filter(user_to=request.user)

    # Mark all notifications as seen
    notifications_reservation.update(seen=True)
    notifications.update(seen=True)
    notifications_reservation_group.update(seen=True)
    notifications_group.update(seen=True)
    Custom_Notifications.update(seen=True)

    # Serialize each queryset
    serializer1 = Notifications_reservationSerializer(notifications_reservation, many=True)
    serializer2 = Notifications_Serializer(notifications, many=True)
    serializer3 = Notifications_group_reservationSerializer(notifications_reservation_group, many=True)
    serializer4 = Notifications_group_Serializer(notifications_group, many=True)
    serializer5 = Custom_Notification_serializer(Custom_Notifications, many=True)

    # Merge and sort all notifications by creation date in descending order
    all_notifications = list(serializer1.data) + list(serializer2.data) + list(serializer3.data) + list(
        serializer4.data) + list(serializer5.data)
    all_notifications.sort(key=lambda x: x['createAt'], reverse=True)

    return Response(all_notifications, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_realestate_notification(request):
    """
    When the user clicks on "تم استلام المهمة" (for a notification of type add_realestate_user),
    this endpoint will:
      - Receive the client id via request.data.
      - Delete all Notifications_group objects having that client.
      - Create a new Notifications_group object with:
         client = old client,
         user_to = currently logged-in user (the one clicking the button),
         notification_type = "got_assigned_add_realestate_admin".
    """
    print(12)
    client_id = request.data.get('client_id')
    if not client_id:
        return Response({"detail": "client_id is required."},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        print(13)

        client = User.objects.get(id=client_id)
    except User.DoesNotExist:
        return Response({"detail": "Client not found."},
                        status=status.HTTP_404_NOT_FOUND)

    # Remove all notifications in Notifications_group for this client
    print(14)

    Notifications_group.objects.filter(client=client).delete()
    print(15)

    # Create a new notification in Notifications_group with the logged in user as user_to.
    new_notification = Notifications_group.objects.create(
        client=client,  # The old client
        user_to=request.user,  # The user who clicked "تم استلام المهمة"
        notification_type="got_assigned_add_realestate_admin"
    )

    NewRealEstate.objects.filter(user=client).update(assigned_handler=request.user)

    # newRealEstate=NewRealEstate.objects.filter(user=client)
    #
    # print("here:", newRealEstate)
    # print('heere',client)
    # newRealEstate.assigned_handler = request.user
    # newRealEstate.save()
    print(16)

    serializer = Notifications_group_Serializer(new_notification)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_reservation_notification(request):
    """
    This view is called when a staff user clicks on "استلام المهمة" for a notification
    of type "ready_to_assign_reservation_admin." It expects both a client_id and a reservation_id
    in the request. It then:
      - Deletes all Notifications_reservation_group objects matching that client AND reservation.
      - Creates a new Notifications_reservation_group record with:
           client = provided client,
           reservation = provided reservation,
           user_to = the staff member who pressed the button,
           notification_type = "accepting_rejecting_reservation_admin"
    """
    print("assign_reservation_notification: entry")
    client_id = request.data.get('client_id')
    reservation_id = request.data.get('reservation_id')

    if not client_id or not reservation_id:
        return Response({"detail": "client_id and reservation_id are required."},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        client = User.objects.get(id=client_id)
    except User.DoesNotExist:
        return Response({"detail": "Client not found."},
                        status=status.HTTP_404_NOT_FOUND)

    try:
        reservation = ReservationPeriod.objects.get(id=reservation_id)
    except ReservationPeriod.DoesNotExist:
        return Response({"detail": "Reservation not found."},
                        status=status.HTTP_404_NOT_FOUND)

    # Delete all notifications (from staff) for this client/reservation
    print("Deleting notifications for client {} and reservation {}".format(client_id, reservation_id))
    Notifications_reservation_group.objects.filter(client=client, reservation=reservation).delete()

    # Create a new notification for the staff member indicating the assignment has been taken
    new_notification = Notifications_reservation_group.objects.create(
        client=client,
        reservation=reservation,
        user_to=request.user,  # The staff member who clicked the button
        notification_type="accepting_rejecting_reservation_admin"
    )
    ReservationPeriod.objects.filter(id=reservation_id).update(assigned_handler=request.user)
    print("New notification created")
    serializer = Notifications_group_reservationSerializer(new_notification)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def handle_reservation_response(request):
    """
    This endpoint handles a response for a reservation assignment notification.
    Expected JSON parameters:
      - reservation_id: (int) the reservation's id.
      - client_id: (int) the client's id.
      - action: (string) either "accepted" or "rejected".
      - reason: (string, optional) provided when action is "rejected".

    It will update the ReservationPeriod status and the assigned_handler,
    remove waiting notifications, and create a new notification for the staff.
    If rejected, it will also log the rejection reason.
    """
    reservation_id = request.data.get('reservation_id')
    client_id = request.data.get('client_id')
    action = request.data.get('action')
    reason = request.data.get('reason', '')

    if not reservation_id or not client_id or not action:
        return Response(
            {"detail": "reservation_id, client_id, and action are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        reservation = ReservationPeriod.objects.get(id=reservation_id)
    except ReservationPeriod.DoesNotExist:
        return Response({"detail": "Reservation not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        client = User.objects.get(id=client_id)
    except User.DoesNotExist:
        return Response({"detail": "Client not found."}, status=status.HTTP_404_NOT_FOUND)

    # Update the reservation status and assign the handler
    if action == "accepted":
        reservation.status = "accepted"
        Notifications_reservation.objects.create(
            user_to=client,
            notification_type='accepted_user',
            reservation=reservation,
        )
    elif action == "rejected":
        reservation.status = "rejected"
        Notifications_reservation.objects.create(
            user_to=client,
            notification_type='rejected_user',
            reservation=reservation,
        )
    else:
        return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)
    reservation.assigned_handler = request.user
    reservation.save()

    # Remove all notifications of type accepting_rejecting_reservation_admin for this reservation & client.
    Notifications_reservation_group.objects.filter(
        client=client,
        reservation=reservation,
        notification_type="accepting_rejecting_reservation_admin"
    ).delete()

    # Create a new notification depending on the action.
    if action == "accepted":
        new_notification = Notifications_reservation_group.objects.create(
            client=client,
            reservation=reservation,
            user_to=request.user,
            notification_type="accepting_reservation_admin"
        )
        Notifications_reservation.objects.create(
            user_to=reservation.realestate.user,
            notification_type='res_accepted_to_Owner',
            reservation=reservation
        )
    else:  # action is "rejected"
        new_notification = Notifications_reservation_group.objects.create(
            client=client,
            reservation=reservation,
            user_to=request.user,
            notification_type="rejecting_reservation_admin"
        )
        Notifications_reservation.objects.create(
            user_to=reservation.realestate.user,
            notification_type='res_rejected_to_Owner',
            reservation=reservation
        )
        # Save the rejection reason.
        ReservationRejection.objects.create(
            reservation=reservation,
            rejected_by=request.user,
            reason=reason
        )

    serializer = Notifications_group_reservationSerializer(new_notification)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import PushToken


@api_view(['POST'])
def save_expo_push_token(request):
    token = request.data.get("expo_push_token")
    user = request.user  # Ensure authentication is handled appropriately

    if token and user and user.is_authenticated:
        PushToken.objects.update_or_create(user=user, defaults={"expo_push_token": token})
        return Response({"message": "Token saved successfully"}, status=status.HTTP_200_OK)

    return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .notification_utils import send_push_notification  # Ensure this import is present


@api_view(['POST'])
def send_push_notification_view(request):
    user = request.user  # Ensure the user is authenticated
    title = request.data.get('title', "hi boddy")
    body = request.data.get('body', "This is a test notification")

    result = send_push_notification(user, title, body)

    if "error" in result:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
def admins_phones(request):
    phons = Phones_Help.objects.all()
    serializer = Phones_Help_serializer(
        phons,
        many=True
    )
    return Response({
        'phons': serializer.data
    }, status=status.HTTP_200_OK)
