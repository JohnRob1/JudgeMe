from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import JMUserCreationForm, JMUserChangeForm
from .models import JMUser


# class JMUserAdmin(UserAdmin):
#     add_form = JMUserCreationForm
#     form = JMUserChangeForm
#     model = JMUser
#     list_display = ["username", ]


# admin.site.register(JMUser, JMUserAdmin)

admin.site.register(JMUser)
