"""
URL configuration for dev project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.urls import path
from kol import views

urlpatterns = [
    path('search/', views.search_view),
    path('info/', views.get_info),
    path('add/', views.add_all_data, name='add_all_data'),
    # path('add/<int:file_id>/', views.add_data, name='add_data'),
    path('', views.search_view),  # Add the root URL pattern
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico'))),  # Optional favicon handling
]
