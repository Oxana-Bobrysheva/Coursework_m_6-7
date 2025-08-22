from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import  reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, DetailView

import subscriptions
from .models import Subscriber, Message, Mailing
from .forms import SubscriberForm, MessageForm, MailingForm


# All views for Subscriber
class SubscriberCreateView(CreateView):
    model = Subscriber
    form_class = SubscriberForm
    template_name = 'subscriptions/subscribe.html'
    success_url = reverse_lazy('subscribers_list')


class SubscriberListView(ListView):
    model = Subscriber
    template_name = "subscriptions/subscribers_list.html"
    context_object_name = 'subscribers'


class SubscriberUpdateView(UpdateView):
    model = Subscriber
    form_class = SubscriberForm
    template_name = 'subscribe.html'
    success_url = reverse_lazy('subscribers_list')


class SubscriberDeleteView(DeleteView):
    model = Subscriber
    template_name = "subscriber_confirm_delete.html"
    success_url = reverse_lazy("subscribers_list")


# All views for Message
class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'subscriptions/message.html'
    success_url = reverse_lazy('messages_list')

class MessageListView(ListView):
    model = Message
    template_name = "subscriptions/messages_list.html"
    context_object_name = 'messages'

class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'message.html'
    success_url = reverse_lazy('messages_list')

class MessageDeleteView(DeleteView):
    model = Message
    template_name = "message_confirm_delete.html"
    success_url = reverse_lazy("messages_list")


# Views for main and contacts pages
def main(request):
    return render(request, 'subscriptions/main.html')

def contacts(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        print(name, phone, message)
        return render(request, 'subscriptions/success.html', {'name': name})
    return render(request, 'subscriptions/contacts.html')

def prices(request):
    return render(request, 'subscriptions/prices.html')


# Views for Mailing
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'subscriptions/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        return Mailing.objects.all().prefetch_related('subscribers')


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'subscriptions/mailing_form.html'
    success_url = reverse_lazy('subscriptions:mailing_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Рассылка успешно создана!')
        return response


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'subscriptions/mailing_form.html'
    success_url = reverse_lazy('subscriptions:mailing_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Рассылка успешно обновлена!')
        return response


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'subscriptions/mailing_confirm_delete.html'
    success_url = reverse_lazy('subscriptions:mailing_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Рассылка успешно удалена!')
        return super().delete(request, *args, **kwargs)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'subscriptions/mailing_detail.html'
    context_object_name = 'mailing'
