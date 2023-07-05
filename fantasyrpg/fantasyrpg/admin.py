from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from fantasyrpg.models import *


class BossEquipmentList(admin.ModelAdmin):
    list_display = ('enemy', 'equip')


class EquipmentList(admin.ModelAdmin):
    list_display = ('name', 'role')


class UserList(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'usertype', 'protagonist')


class HeroList(admin.ModelAdmin):
    list_display = ('name', 'life', 'attack', 'defence', 'equip')


admin.site.register(MyUser, UserList)
admin.site.register(Hero, HeroList)
admin.site.register(Boss)
admin.site.register(Equipment, EquipmentList)
admin.site.register(BossEquipment, BossEquipmentList)
