from rest_framework import serializers
from django.contrib.auth import get_user_model
import math
from .models import (
    Notifications_group,
    Notifications_reservation_group,
    Notifications,
    Notifications_reservation,
    ReservationPeriod,
    RealEstate_Images,
    Extras,
    Basics,
    RealEstate,
    Review,
    NewRealEstate,
    Second_Review,
    Favourits,
    Custom_Notification,
    Phones_Help,
)

User = get_user_model()  # Use the custom user model


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']  # Add more fields here if needed


class RealEstateImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealEstate_Images
        fields = ['image']  # You can add more fields if necessary.


# If you have renamed 'describtion' to 'description' in your models, update these serializers accordingly.
class BasicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Basics
        fields = ['describtion', 'photo']  # Change to ['description', 'photo'] if field renamed.


class ExtrasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extras
        fields = ['describtion', 'photo']  # Change to ['description', 'photo'] if field renamed.


class RealEstateSerializer(serializers.ModelSerializer):
    is_favorite = serializers.SerializerMethodField()
    price_with_benefit = serializers.SerializerMethodField()
    holiday_price_with_benefit = serializers.SerializerMethodField()
    ead_price_with_benefit = serializers.SerializerMethodField()
    basics = BasicsSerializer(many=True, read_only=True)
    extras = ExtrasSerializer(many=True, read_only=True)
    images = RealEstateImagesSerializer(many=True, read_only=True)

    class Meta:
        model = RealEstate
        fields = [
            'id', 'price', 'price_with_benefit', 'holiday_price', 'holiday_price_with_benefit',
            'ead_price', 'ead_price_with_benefit', 'city', 'town', 'type',
            'max_members', 'rooms', 'bathrooms', 'period', 'ratings', 'photo',
            'is_favorite', 'basics', 'extras', 'images',
            'latitude', 'longitude', 'describtion', 'checkout', 'checkin', 'cars'
        ]

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favourites_list.filter(user=request.user).exists()
        return False

    def get_price_with_benefit(self, obj):
        return math.ceil(float(obj.price) * 1.15)

    def get_holiday_price_with_benefit(self, obj):
        return math.ceil(float(obj.holiday_price) * 1.15)

    def get_ead_price_with_benefit(self, obj):
        return math.ceil(float(obj.ead_price) * 1.15)


class NewRealEstateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewRealEstate
        fields = "__all__"
        read_only_fields = ('user',)


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = "__all__"


class SecondReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Second_Review
        fields = "__all__"


class MYRESERVATIONSerializer(serializers.ModelSerializer):
    is_favorite = serializers.SerializerMethodField()
    price_with_benefit = serializers.SerializerMethodField()

    class Meta:
        model = RealEstate
        fields = ['id', 'photo', 'type'
            , 'period', 'ratings', 'price', 'town', 'city', 'is_favorite', 'price_with_benefit'
                  ]

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favourites_list.filter(user=request.user).exists()
        return False

    def get_price_with_benefit(self, obj):
        return math.ceil(float(obj.price) * 1.15)

class FavouritSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourits
        fields = "__all__"


#
# class MyReservationsSerializer(serializers.ModelSerializer):
#     realestate = RealEstateSerializer(read_only=True)
#     class Meta:
#         model = MyReservations
#         fields = '__all__'


class ReservationPeriodSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_phone = serializers.CharField(source='user.person.phone', read_only=True)

    class Meta:
        model = ReservationPeriod
        fields = ['id', 'user_name', 'user_phone', 'start_date', 'end_date', 'status']


# Remove duplicate UserSerializer definition if present.

User = get_user_model()


class Notifications_reservationSerializer(serializers.ModelSerializer):
    propertyId = serializers.SerializerMethodField()
    startDate = serializers.SerializerMethodField()
    endDate = serializers.SerializerMethodField()
    userName = serializers.SerializerMethodField()
    userPhone = serializers.SerializerMethodField()
    rejectionReason = serializers.SerializerMethodField()

    class Meta:
        model = Notifications_reservation
        fields = (
            'id',
            'user_to',
            'notification_type',
            'reservation',
            'createAt',  # updated field name
            'seen',
            'propertyId',
            'startDate',
            'endDate',
            'userName',  # added field
            'userPhone',  # added field
            'rejectionReason',  # new field
        )

    def get_propertyId(self, obj):
        if obj.reservation and obj.reservation.realestate:
            return obj.reservation.realestate.id
        return None

    def get_startDate(self, obj):
        if obj.reservation:
            return obj.reservation.start_date
        return None

    def get_endDate(self, obj):
        if obj.reservation:
            return obj.reservation.end_date
        return None

    def get_userName(self, obj):
        """
        Returns the name from the reservation's user.
        It uses the associated Person if available; otherwise, it falls back to the username.
        """
        if obj.reservation and obj.reservation.user:
            if hasattr(obj.reservation.user, 'person') and obj.reservation.user.person:
                return obj.reservation.user.person.name
            return obj.reservation.user.username
        return None

    def get_userPhone(self, obj):
        """
        Returns the user's phone number from the related Person instance.
        """
        if obj.reservation and obj.reservation.user:
            if hasattr(obj.reservation.user, 'person') and obj.reservation.user.person:
                return obj.reservation.user.person.phone
        return None

    def get_rejectionReason(self, obj):
        """
        Retrieves and returns the rejection reason from the first related ReservationRejection.
        """
        if obj.reservation:
            rejections = obj.reservation.rejections.all()
            if rejections.exists():
                return rejections.first().reason
        return ""


class Notifications_Serializer(serializers.ModelSerializer):
    userName = serializers.SerializerMethodField()
    userPhone = serializers.SerializerMethodField()

    class Meta:
        model = Notifications
        fields = (
            'id',
            'user_to',
            'notification_type',
            'createAt',  # updated field name
            'seen',
            'userName',
            'userPhone',
        )

    def get_userName(self, obj):
        if obj.user_to:
            if hasattr(obj.user_to, 'person') and obj.user_to.person:
                return obj.user_to.person.name
            return obj.user_to.username
        return ''

    def get_userPhone(self, obj):
        if obj.user_to:
            if hasattr(obj.user_to, 'person') and obj.user_to.person:
                return obj.user_to.person.phone
        return ''


class Notifications_group_reservationSerializer(serializers.ModelSerializer):
    propertyId = serializers.SerializerMethodField()
    startDate = serializers.SerializerMethodField()
    endDate = serializers.SerializerMethodField()
    userName = serializers.SerializerMethodField()
    userPhone = serializers.SerializerMethodField()
    rejectionReason = serializers.SerializerMethodField()

    class Meta:
        model = Notifications_reservation_group
        fields = (
            'id',
            'user_to',
            'notification_type',
            'reservation',
            'createAt',  # updated field name
            'seen',
            'propertyId',
            'startDate',
            'endDate',
            'client',
            'userName',
            'userPhone',
            'rejectionReason',  # new field
        )

    def get_propertyId(self, obj):
        if obj.reservation and obj.reservation.realestate:
            return obj.reservation.realestate.id
        return None

    def get_startDate(self, obj):
        if obj.reservation:
            return obj.reservation.start_date
        return None

    def get_endDate(self, obj):
        if obj.reservation:
            return obj.reservation.end_date
        return None

    def get_userName(self, obj):
        if obj.client:
            if hasattr(obj.client, 'person') and obj.client.person:
                return obj.client.person.name
            return obj.client.username
        return ''

    def get_userPhone(self, obj):
        if obj.client:
            if hasattr(obj.client, 'person') and obj.client.person:
                return obj.client.person.phone
        return ''

    def get_rejectionReason(self, obj):
        """
        Look up a rejection reason on the related reservation.
        Returns the reason from the first ReservationRejection (if any).
        """
        if obj.reservation:
            rejections = obj.reservation.rejections.all()  # assuming related_name="rejections"
            if rejections.exists():
                return rejections.first().reason
        return ""


class Notifications_group_Serializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(read_only=True)
    userName = serializers.SerializerMethodField()
    userPhone = serializers.SerializerMethodField()

    class Meta:
        model = Notifications_group
        fields = (
            'id',
            'user_to',
            'notification_type',
            'createAt',  # updated field name
            'seen',
            'client',
            'userName',
            'userPhone',
        )

    def get_userName(self, obj):
        if obj.client:
            if hasattr(obj.client, 'person') and obj.client.person:
                return obj.client.person.name
            return obj.client.username
        return ''

    def get_userPhone(self, obj):
        if obj.client:
            if hasattr(obj.client, 'person') and obj.client.person:
                return obj.client.person.phone
        return ''


class Custom_Notification_serializer(serializers.ModelSerializer):
    userName = serializers.SerializerMethodField()
    userPhone = serializers.SerializerMethodField()

    class Meta:
        model = Custom_Notification
        fields = (
            'id',
            'user_to',
            'notification_type',
            'createAt',  # updated field name
            'seen',
            'userName',
            'userPhone',
            'message'
        )

    def get_userName(self, obj):
        if obj.user_to:
            if hasattr(obj.user_to, 'person') and obj.user_to.person:
                return obj.user_to.person.name
            return obj.user_to.username
        return ''

    def get_userPhone(self, obj):
        if obj.user_to:
            if hasattr(obj.user_to, 'person') and obj.user_to.person:
                return obj.user_to.person.phone
        return ''


class Phones_Help_serializer(serializers.ModelSerializer):
    class Meta:
        model = Phones_Help
        fields = "__all__"