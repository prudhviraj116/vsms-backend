from django.contrib import admin
from.models import Staff_tabel,Staff_depatments,User
# from .models import staff,Staffdepartments
# Register your models here.
from django.contrib.auth.admin import UserAdmin

class Usermodel(UserAdmin):
    pass

admin.site.register(Staff_tabel)
admin.site.register(Staff_depatments)
admin.site.register(User,Usermodel)