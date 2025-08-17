from django.views.generic import TemplateView
from django.urls import path
from .views import SubscriberCreateView, SubscriberUpdateView, SubscriberListView, SubscriberDeleteView, \
    MessageListView, MessageCreateView, MessageUpdateView, MessageDeleteView

urlpatterns = [
    path('subscribers/', SubscriberListView.as_view(), name='subscribers_list'),
    path('subscribers/add/', SubscriberCreateView.as_view(), name='create_subscriber'),
    path('subscribers/edit/<int:pk>/', SubscriberUpdateView.as_view(), name='update_subscriber'),
    path('subscribers/delete/<int:pk>/', SubscriberDeleteView.as_view(), name='delete_subscriber'),

    path('messages/', MessageListView.as_view(), name='messages_list'),
    path('messages/add/', MessageCreateView.as_view(), name='create_message'),
    path('messages/edit/<int:pk>/', MessageUpdateView.as_view(), name='update_message'),
    path('messages/delete/<int:pk>/', MessageDeleteView.as_view(), name='delete_message'),
    ]