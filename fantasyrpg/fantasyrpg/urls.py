"""fantasyrpg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from fantasyrpg import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('signup/', views.signup, name="signup"),
    path('first_creation_hero/', views.first_creation_hero, name="first_creation_hero"),
    path('login/', views.loginPage, name="loginPage"),
    path('logout/', views.logoutUser, name="logout"),
    path('user_home/', views.user_home, name='user_home'),
    path('user_home/change_equipment', views.change_equipment, name='change_equipment'),
    path('user_home/fight', views.fight, name='fight'),
    path('gamedev_home/', views.gamedev_home, name='gamedev_home'),
    path('gamedev_home/update_equipment', views.update_equipment, name='update_equipment'),
    path('gamedev_home/update_boss', views.update_boss, name='update_boss'),
    path('gamedev_home/add_equipment', views.add_equipment, name='add_equipment'),
    path('gamedev_home/add_boss', views.add_boss, name='add_boss'),
    path('gamedev_home/remove_equipment', views.remove_equipment, name='remove_equipment'),
    path('gamedev_home/remove_boss', views.remove_boss, name='remove_boss')
]
