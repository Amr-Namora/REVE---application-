from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser,Person


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'is_staff', 'is_active', 'get_person_name', 'get_person_city', 'get_person_phone')
    list_filter = ('is_staff', 'is_active')
    ordering = ('username',)
    search_fields = ['username', 'person__name', 'person__phone']  # This will search through related Person fields

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Permissions'), {
            'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important dates'), {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'password1', 'password2', 'is_staff', 'is_active'),
            },
        ),
    )

    # Custom method to get related Person data
    def get_person_name(self, obj):
        return obj.person.name if hasattr(obj, 'person') and obj.person else '-'

    get_person_name.short_description = 'Person Name'

    def get_person_city(self, obj):
        return obj.person.city if hasattr(obj, 'person') and obj.person else '-'

    get_person_city.short_description = 'City'

    def get_person_phone(self, obj):
        return obj.person.phone if hasattr(obj, 'person') and obj.person else '-'

    get_person_phone.short_description = 'Phone'


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'phone', 'user')
    search_fields = ('name', 'phone', 'city')