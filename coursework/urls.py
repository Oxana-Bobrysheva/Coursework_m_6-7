from django.contrib import admin
from django.urls import path, include
from subscriptions.views import main_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include('subscriptions.urls')),
    path('accounts/', include('allauth.urls')),
]
