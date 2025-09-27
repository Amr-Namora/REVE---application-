from django.utils import timezone

from django.db import models
from django.conf import settings

class Extras(models.Model):
    describtion = models.CharField(max_length=50)  # renamed field for clarity
    photo = models.ImageField(upload_to='photo/Extras', null=True, blank=True)

    def __str__(self):
        return self.describtion


class Basics(models.Model):
    describtion = models.CharField(max_length=50)  # renamed field
    photo = models.ImageField(upload_to='photo/Basics', null=True, blank=True)  # different folder if desired

    def __str__(self):
        return self.describtion





class RealEstate(models.Model):
    TYPES = (
        ('مزرعة', 'مزرعة'),
        ('فيلّا', 'فيلّا'),
        ('شقة', 'شقة'),
    )
    CITIES = (
        ('خارج سوريا', 'خارج سوريا'),
        ('ادلب', 'ادلب'),
        ('دمشق', 'دمشق'),
        ('حلب', 'حلب'),
        ('ريف دمشق', 'ريف دمشق'),
        ('حماه', 'حماه'),
        ('حمص', 'حمص'),
        ('درعا', 'درعا'),
        ('القنيطرة', 'القنيطرة'),
        ('السويداء', 'السويداء'),
        ('دير الزور', 'دير الزور'),
        ('القامشلي', 'القامشلي'),
        ('الحسكة', 'الحسكة'),
        ('اللاذقية', 'اللاذقية'),
        ('طرطوس', 'طرطوس'),
    )
    PERIODS = (
        ('باليوم', 'باليوم'),
        ('بالشهر', 'بالشهر'),
    )
    TORF = (
        ('Yes', 'Yes'),
        ('No', 'No')
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='صاحب العقار',
        related_name='myrealestates'
    )
    basics = models.ManyToManyField('Basics')
    extras = models.ManyToManyField('Extras')
    price = models.DecimalField(decimal_places=2, null=True, max_digits=10, verbose_name='السعر')
    city = models.CharField(max_length=30, null=True, choices=CITIES, verbose_name='المحافظة')
    town = models.CharField(max_length=30, default="", verbose_name='المنطقة')
    type = models.CharField(max_length=30, null=True, choices=TYPES, verbose_name='نوع العقار')
    max_members = models.IntegerField(default=0, verbose_name='عدد الاشخاص المسموح')
    rooms = models.IntegerField(default=0, verbose_name='عدد الغرف')
    bathrooms = models.IntegerField(default=0, verbose_name='عدد الحمامات')
    cars=models.IntegerField(default=0, verbose_name='عدد السيارات المتاحة في الكراج')
    period = models.CharField(max_length=30, null=True, choices=PERIODS, verbose_name='باليوم او بالشهر؟')
    ratings = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    photo = models.ImageField(upload_to='photo/properties', null=True, blank=True)
    describtion = models.TextField(default='')  # renamed from 'describtion'
    latitude = models.FloatField(null=True, blank=True, verbose_name='خط العرض')
    longitude = models.FloatField(null=True, blank=True, verbose_name='خط الطول')
    ead_price= models.DecimalField(decimal_places=2,null=True, max_digits=10, verbose_name='السعر بالعيد')
    holiday_price= models.DecimalField(decimal_places=2,null=True, max_digits=10, verbose_name='السعر بالعطلة')
    checkin=models.CharField(max_length=40,null=True,blank=True,verbose_name='بداية الحجز')
    checkout=models.CharField(max_length=40,null=True,blank=True,verbose_name='انتهاء الحجز')
    name_of_realestate=models.CharField(max_length=50,null=True,default=' ',verbose_name='اسم المزرعة')
    def __str__(self):
        return self.name_of_realestate


class RealEstate_Images(models.Model):
    image = models.ImageField(upload_to='photos/properties', blank=True, null=True, verbose_name='الصورة')
    realestate = models.ForeignKey(
        RealEstate,
        null=True,
        on_delete=models.CASCADE,
        related_name='images'
    )
    def __str__(self):
        return self.realestate.name_of_realestate


class Review(models.Model):
    real_estate = models.ForeignKey(
        'RealEstate',
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        related_name='review'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL
    )
    rating = models.IntegerField(default=0)
    comment = models.TextField(max_length=1000, default="", blank=False)
    createAt = models.DateTimeField(default=timezone.now, blank=True, null=True)


    def __str__(self):
        return self.comment


class Second_Review(models.Model):
    real_estate = models.ForeignKey(
        'RealEstate',
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        related_name='second_review'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL
    )
    rating = models.IntegerField(default=0)
    comment = models.TextField(max_length=1000, default="", blank=False)
    createAt = models.DateTimeField(default=timezone.now, blank=True, null=True)

    def __str__(self):
        return self.comment


class ReservationPeriod(models.Model):
    STATUS_CHOICES = (
       ('pending', 'pending'),
       ('rejected', 'rejected'),
       ('accepted', 'accepted'),
       ('DayOff', 'DayOff'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservation_periods',
        verbose_name='صاحب الحجز'
    )
    realestate = models.ForeignKey(
        'RealEstate',
        on_delete=models.CASCADE,
        related_name='realestate'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    createAt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(default='pending', max_length=30, choices=STATUS_CHOICES)
    # New field to record which handler (if any) has taken the reservation:
    assigned_handler = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_reservations"
    )

    def __str__(self):
        return f"{self.realestate} reserved from {self.start_date} to {self.end_date}"





class NewRealEstate(models.Model):
    TYPES = (
        ('مزرعة', 'مزرعة'),
        ('فيلّا', 'فيلّا'),
        ('شقة', 'شقة'),
    )
    ADDRESS_CHOICES = (
        ('خارج سوريا', 'خارج سوريا'),
        ('ادلب', 'ادلب'),
        ('دمشق', 'دمشق'),
        ('حلب', 'حلب'),
        ('ريف دمشق', 'ريف دمشق'),
        ('حماه', 'حماه'),
        ('حمص', 'حمص'),
        ('درعا', 'درعا'),
        ('القنيطرة', 'القنيطرة'),
        ('السويداء', 'السويداء'),
        ('دير الزور', 'دير الزور'),
        ('القامشلي', 'القامشلي'),
        ('الحسكة', 'الحسكة'),
        ('اللاذقية', 'اللاذقية'),
        ('طرطوس', 'طرطوس'),
    )
    city = models.CharField(max_length=30, blank=True, null=True, choices=ADDRESS_CHOICES, verbose_name='المحافظة')
    town = models.CharField(max_length=30, blank=True, null=True, verbose_name='المدينة او البلدة')
    type = models.CharField(max_length=30, blank=True, null=True, choices=TYPES, verbose_name='نوع العقار')
    notes = models.CharField(max_length=500, blank=True, null=True, verbose_name='ملاحظات')

    # Use OneToOneField if only one real estate per user is allowed,
    # otherwise consider a ForeignKey.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    assigned_handler = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_add_realestate"
    )
    def __str__(self):
        return self.user.username if self.user else "No User"


class Favourits(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='الزبون',
                             related_name='favourites')
    realestate = models.ForeignKey('RealEstate', on_delete=models.CASCADE, verbose_name='العقار',
                                   related_name='favourites_list')

    def __str__(self):
        return self.user.username if self.user else "No User"


class ReservationRejection(models.Model):
    reservation = models.ForeignKey(
        'ReservationPeriod',
        on_delete=models.CASCADE,
        related_name="rejections"
    )
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservation_rejections"
    )
    reason = models.TextField()
    createAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Check if rejected_by exists
        user_str = self.rejected_by.username if self.rejected_by else "Unknown User"
        return f"Rejection for reservation {self.reservation.id} by {user_str}"


class Custom_Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = (
        ('write_message', 'write_message'),
    )
    user_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        related_name='Custom_Notification'
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='write_message'  # Or change choices to include 'welcome'
    )
    message=models.TextField(verbose_name='الرسالة')
    createAt = models.DateTimeField(null=True, auto_now_add=True)
    seen = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification to {self.user_to}"


class Notifications_reservation(models.Model):
    NOTIFICATION_TYPE_CHOICES = (
        ('accepted_user', 'accepted_user'),
        ('rejected_user', 'rejected_user'),
        ('still_pending_user', 'still_pending_user'),
        ('res_accepted_to_Owner','res_accepted_to_Owner'),
        ('res_rejected_to_Owner','res_rejected_to_Owner'),
        ('res_pending_to_Owner','res_pending_to_Owner'),
    )

    user_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        related_name='notifications_reservation_to'
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='still_pending_user'
    )
    # Optional link to the reservation (if applicable)
    reservation = models.ForeignKey(
        'ReservationPeriod',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='notifications_reservation'
    )
    createAt = models.DateTimeField(null=True, auto_now_add=True)
    seen = models.BooleanField(default=False)  # Track if the notification was viewed

    def __str__(self):
        return f"Notification to {self.user_to.username if self.user_to else 'Unknown User'}"


class Notifications(models.Model):
    NOTIFICATION_TYPE_CHOICES = (
        ('welcome_user', 'welcome_user'),
        ('add_realestate_user', 'add_realestate_user'),
    )
    # If you need a sender, consider uncommenting and adjusting this field:
    # user_from = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     null=True,
    #     on_delete=models.PROTECT,
    #     related_name='notifications_from'
    # )
    user_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        related_name='notifications_to'
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='welcome_user'
    )
    createAt = models.DateTimeField(null=True, auto_now_add=True)
    seen = models.BooleanField(default=False)  # Track if the notification was viewed

    def __str__(self):
        return f"Notification to {self.user_to.username if self.user_to else 'Unknown User'}"



class Notifications_reservation_group(models.Model):
    NOTIFICATION_TYPE_CHOICES = (
        ('ready_to_assign_reservation_admin', 'ready_to_assign_reservation_admin'),
        ('accepting_rejecting_reservation_admin', 'accepting_rejecting_reservation_admin'),
        ('accepting_reservation_admin', 'accepting_reservation_admin'),
        ('rejecting_reservation_admin', 'rejecting_reservation_admin'),
        # Optionally, if you wish to have 'still pending' as a valid default:
        # ('still pending', 'still pending'),
    )

    user_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        related_name='notifications_reservation_to_group'
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        related_name='client_reservation'
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='ready_to_assign_reservation_admin'  # Change default to one of the valid choices, or add 'still pending' in the tuple.
    )
    # Optional link to the reservation (if applicable).
    reservation = models.ForeignKey(
        'ReservationPeriod',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='notifications_reservation_group'
    )
    createAt = models.DateTimeField(null=True, auto_now_add=True)
    seen = models.BooleanField(default=False)  # Field to track if the notification was viewed

    def __str__(self):
        return f"Notification to {self.user_to}"


class Notifications_group(models.Model):
    NOTIFICATION_TYPE_CHOICES = (
        ('ready_to_assign_add_realestate_admin', 'ready_to_assign_add_realestate_admin'),
        ('got_assigned_add_realestate_admin', 'got_assigned_add_realestate_admin'),
        # Optionally add ('welcome', 'welcome') if you intend to use that as the default.
    )
    user_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        related_name='notifications_to_group'
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        related_name='client_group'
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='ready_to_assign_add_realestate_admin'  # Or change choices to include 'welcome'
    )
    createAt = models.DateTimeField(null=True, auto_now_add=True)
    seen = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification to {self.user_to}"



class Phones_Help(models.Model):
    phone=models.CharField(max_length=30,null=True,verbose_name='رقم الادمن')
    name=models.CharField(max_length=30,null=True,verbose_name='اسم الادمن')
    def __str__(self):
        return self.name


class PushToken(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    expo_push_token = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username} - {self.expo_push_token}"
