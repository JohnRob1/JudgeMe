from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import JMUserCreationForm, JMUserChangeForm
from .models import JMUser

admin.site.register(JMUser)


class JMUserAdmin(UserAdmin):
    add_form = JMUserCreationForm
    form = JMUserChangeForm
    model = JMUser
    list_display = ('username')
    list_filter = ('username')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(JMUser, JMUserAdmin)
