from django.views.generic import TemplateView
from django.urls import path

from . import views
from .views import (
    SubscriberCreateView, SubscriberUpdateView, SubscriberListView, SubscriberDeleteView,
    MessageListView, MessageCreateView, MessageUpdateView, MessageDeleteView,
    MailingListView, MailingCreateView, MailingDetailView, MailingUpdateView, MailingDeleteView,
    SendMailingView, MailingAttemptListView, MailingStatsView,
    UserListView, UserToggleActiveView, MailingToggleActiveView, mailing_toggle_active,
)

app_name = 'subscriptions'

urlpatterns = [
    path("", views.index, name="main"),
    path('contacts/', views.contacts, name="contacts"),
    path('prices/', views.prices, name='prices'),

    path('subscribers/', SubscriberListView.as_view(), name='subscribers_list'),
    path('subscribers/add/', SubscriberCreateView.as_view(), name='create_subscriber'),
    path('subscribers/edit/<int:pk>/', SubscriberUpdateView.as_view(), name='update_subscriber'),
    path('subscribers/delete/<int:pk>/', SubscriberDeleteView.as_view(), name='delete_subscriber'),

    path('messages/', MessageListView.as_view(), name='messages_list'),
    path('messages/add/', MessageCreateView.as_view(), name='create_message'),
    path('messages/edit/<int:pk>/', MessageUpdateView.as_view(), name='update_message'),
    path('messages/delete/<int:pk>/', MessageDeleteView.as_view(), name='delete_message'),

    path('mailings/', MailingListView.as_view(), name='mailing_list'),
    path('mailings/create/', MailingCreateView.as_view(), name='mailing_create'),
    path('mailings/<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('mailings/<int:pk>/edit/', MailingUpdateView.as_view(), name='mailing_edit'),
    path('mailings/<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing_delete'),

    path('mailings/<int:pk>/send/', SendMailingView.as_view(), name='send_mailing'),
    path('mailings/attempts/', MailingAttemptListView.as_view(), name='mailing_attempts'),
    path('mailings/<int:pk>/attempts/', MailingAttemptListView.as_view(), name='mailing_attempt_list'),

    # Статистика
    path('stats/', MailingStatsView.as_view(), name='mailing_stats'),

    # Управление пользователями (только для менеджеров)
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/toggle/', UserToggleActiveView.as_view(), name='user_toggle_active'),

    # Отключение рассылок (только для менеджеров)
    path('mailings/<int:pk>/toggle/', MailingToggleActiveView.as_view(), name='mailing_toggle_active'),
    path('mailings/<int:pk>/toggle/', mailing_toggle_active, name='mailing_toggle_active')
    ]
