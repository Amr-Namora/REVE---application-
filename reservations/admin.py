from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Phones_Help,Custom_Notification,PushToken,ReservationRejection, Notifications_group,Notifications_reservation_group,Notifications_reservation,Notifications,ReservationPeriod,Second_Review,RealEstate_Images,NewRealEstate,Review,RealEstate,Extras,Favourits,Basics
from django.contrib.auth.admin import UserAdmin

admin.site.register(Review)
admin.site.register(Phones_Help)

admin.site.register(PushToken)
admin.site.register(Custom_Notification)
admin.site.register(Notifications_reservation)
admin.site.register(Notifications_group)
admin.site.register(Notifications_reservation_group)
admin.site.register(Notifications)
admin.site.register(Extras)
admin.site.register(Favourits)
admin.site.register(Basics)
admin.site.register(Second_Review)


@admin.register(ReservationPeriod)
class ReservationPeriodAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date','get_person_owner_name','get_person_owner_phone', 'get_person_name', 'get_person_phone')
    # search_fields = ()

    def get_person_owner_name(self, obj):
        return obj.realestate.user.person.name if hasattr(obj.realestate.user, 'person') and obj.realestate.user.person else '-'

    get_person_owner_name.short_description = 'اسم صاحب العقار'


    def get_person_owner_phone(self, obj):
        return obj.realestate.user.person.phone if hasattr(obj.realestate.user, 'person') and obj.realestate.user.person else '-'

    get_person_owner_phone.short_description = 'رقم صاحب العقار'

    def get_person_name(self, obj):
        return obj.user.person.name if hasattr(obj.user, 'person') and obj.user.person else '-'

    get_person_name.short_description = 'اسم الزبون'


    def get_person_phone(self, obj):
        return obj.user.person.phone if hasattr(obj.user, 'person') and obj.user.person else '-'

    get_person_phone.short_description = 'رقم الزبون'



@admin.register(NewRealEstate)
class NewRealEstateAdmin(admin.ModelAdmin):
    list_display = ('city', 'town', 'type','get_person_name', 'get_person_phone')
    # search_fields = ()

    def get_person_name(self, obj):
        return obj.user.person.name if hasattr(obj.user, 'person') and obj.user.person else '-'

    get_person_name.short_description = 'Person Name'


    def get_person_phone(self, obj):
        return obj.user.person.phone if hasattr(obj.user, 'person') and obj.user.person else '-'

    get_person_phone.short_description = 'Phone'



@admin.register(ReservationRejection)
class ReservationRejectionAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'get_person_name', 'get_person_phone','rejected_by')
    # search_fields = ()

    def get_person_name(self, obj):
        return obj.reservation.user.person.name if hasattr(obj.reservation.user, 'person') and obj.reservation.user.person else '-'

    get_person_name.short_description = 'اسم صاحب العقار'


    def get_person_phone(self, obj):
        return obj.reservation.user.person.phone if hasattr(obj.reservation.user, 'person') and obj.reservation.user.person else '-'

    get_person_phone.short_description = 'رقم صاحب العقار'


    # def get_person_owner_name(self, obj):
    #     return obj.user.person.name if hasattr(obj.user, 'person') and obj.user.person else '-'
    #
    # get_person_name.short_description = 'اسم الزبون'
    #
    #
    # def get_person_owner_phone(self, obj):
    #     return obj.user.person.phone if hasattr(obj.user, 'person') and obj.user.person else '-'
    #
    # get_person_phone.short_description = 'رقم الزبون'


@admin.register(RealEstate_Images)
class RealEstate_ImagesAdmin(admin.ModelAdmin):
    autocomplete_fields = ['realestate']
    search_fields = ['realestate__name_of_realestate']
    list_display = ['realestate__name_of_realestate','get_person_name']

    def get_person_name(self, obj):
        return obj.realestate.user.person.name if hasattr(obj.realestate.user, 'person') and obj.realestate.user.person else '-'

    get_person_name.short_description = 'الاسم'


class RealEstate_admin(admin.ModelAdmin):
    # this will show the products as table
    # name     price      active
    # a         11         T
    # b         10         T
    #  if you turn it to  list_display =['name','active','price']
    # the order of the table will chang
    # name       active        price
    # a            T           10
    # b            T           11

    list_display = ('name_of_realestate','city','town', 'get_person_name', 'get_person_phone')

    # list_editable = ['town','city',  'price']
    # now you can edit the (active or not) of every product easier
    # you can put      list_editable = ['name','active',...]
    # but you can not put any thing you put in list_display_links
    # which means you can not put 'name' in list_editable , because you put it i in list_display_links
    search_fields = ['town','id', 'city','name_of_realestate', 'price']
    # will put box to search among the products based on name
    list_filter = ['city','type']

    # will create filters based on category and price
    # fields = ['name', 'price', 'category']
    # when you click on the name you will see all information for that products
    # but with this line now you will see just name , price and category


    autocomplete_fields = ['user']

    def get_person_name(self, obj):
        return obj.user.person.name if hasattr(obj.user, 'person') and obj.user.person else '-'

    get_person_name.short_description = 'الاسم'


    def get_person_phone(self, obj):
        return obj.user.person.phone if hasattr(obj.user, 'person') and obj.user.person else '-'

    get_person_phone.short_description = 'الرقم'
admin.site.register(RealEstate, RealEstate_admin)
# don't forget to do this
