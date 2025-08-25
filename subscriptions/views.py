from django.contrib import messages
from django.core.mail import send_mail
#from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import  reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, DetailView

from .models import Subscriber, Message, Mailing
from .forms import SubscriberForm, MessageForm, MailingForm
from .services import send_mailing


# All views for Subscriber
class SubscriberCreateView(CreateView):
    model = Subscriber
    form_class = SubscriberForm
    template_name = 'subscriptions/subscribe.html'
    success_url = reverse_lazy('subscriptions:subscribers_list')


class SubscriberListView(ListView):
    model = Subscriber
    template_name = "subscriptions/subscribers_list.html"
    context_object_name = 'subscribers'


class SubscriberUpdateView(UpdateView):
    model = Subscriber
    form_class = SubscriberForm
    template_name = 'subscriptions/subscribe.html'
    success_url = reverse_lazy('subscriptions:subscribers_list')


class SubscriberDeleteView(DeleteView):
    model = Subscriber
    template_name = "subscriptions/subscriber_confirm_delete.html"
    success_url = reverse_lazy("subscriptions:subscribers_list")


# All views for Message
class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'subscriptions/message.html'
    success_url = reverse_lazy('subscriptions:messages_list')

class MessageListView(ListView):
    model = Message
    template_name = "subscriptions/messages_list.html"
    context_object_name = 'messages'

class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'subscriptions/message.html'
    success_url = reverse_lazy('subscriptions:messages_list')

class MessageDeleteView(DeleteView):
    model = Message
    template_name = "subscriptions/message_confirm_delete.html"
    success_url = reverse_lazy("subscriptions:messages_list")


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
class MailingListView(ListView):
    model = Mailing
    template_name = 'subscriptions/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        return Mailing.objects.all().prefetch_related('subscribers')


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'subscriptions/mailing_form.html'
    success_url = reverse_lazy('subscriptions:mailing_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Рассылка успешно создана!')
        return response


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'subscriptions/mailing_form.html'
    success_url = reverse_lazy('subscriptions:mailing_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Рассылка успешно обновлена!')
        return response


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'subscriptions/mailing_confirm_delete.html'
    success_url = reverse_lazy('subscriptions:mailing_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Рассылка успешно удалена!')
        return super().delete(request, *args, **kwargs)


class MailingDetailView(DetailView):
    model = Mailing
    template_name = 'subscriptions/mailing_detail.html'
    context_object_name = 'mailing'

class SendMailingView(View):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        # Проверяем, что время начала уже наступило и время окончания не прошло
        if timezone.now() >= mailing.start_time:
            if timezone.now() > mailing.end_time:
                messages.error(request, 'Рассылка уже завершена и не может быть отправлена!')
                return redirect('subscriptions:mailing_detail', pk=mailing.pk)

            # Устанавливаем статус "запущена" перед отправкой
            mailing.status = 'started'
            mailing.save()

            # Логика отправки сообщений
            for subscriber in mailing.subscribers.all():
                send_mail(
                    mailing.message.subject_of_the_letter,
                    mailing.message.letter,
                    'bobrysheva_oxana@mail.ru',
                    [subscriber.email],
                    fail_silently=False,
                )
                # Например, отправка электронной почты
                print(f"Отправка сообщения '{mailing.message.subject_of_the_letter}' на {subscriber.email}")

            mailing.save()
            messages.success(request, 'Рассылка успешно отправлена!')
        else:
            messages.error(request, 'Рассылка не может быть отправлена до начала!')

        return redirect('subscriptions:mailing_detail', pk=mailing.pk)

    def start_mailing(request, mailing_id):
        mailing = Mailing.objects.get(id=mailing_id)
        send_mailing(mailing)
        return redirect('mailing_list')
