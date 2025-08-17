from django.urls import  reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from .models import Subscriber, Message
from .forms import SubscriberForm

# All views for Subscriber
class SubscriberCreateView(CreateView):
    model = Subscriber
    form_class = SubscriberForm
    template_name = 'subscribe.html'
    success_url = reverse_lazy('subscribers_list')


class SubscriberListView(ListView):
    model = Subscriber
    template_name = "subscribers_list.html"
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
    template_name = 'message.html'
    success_url = reverse_lazy('messages_list')

class MessageListView(ListView):
    model = Message
    template_name = "messages_list.html"
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