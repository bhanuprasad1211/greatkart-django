from django.contrib import admin
from .models import Accounts
from django.contrib.auth.admin import UserAdmin
# Register your models here.

class AccountAdmin(UserAdmin) :
    list_display=('email','first_name','last_name','username','last_login','join_date','is_active')
    # readonly_fields=('password',) to disable reset password option

    list_display_links=('email','first_name','last_name')

    # readonly_fields=('last_login','join_date')

    ordering=('join_date',)

    filter_horizontal=()
    list_filter=()
    fieldsets=()
admin.site.register(Accounts,AccountAdmin)