from django.urls import  reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from .models import Subscriber
from .forms import SubscriberForm

# Create your views here.
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