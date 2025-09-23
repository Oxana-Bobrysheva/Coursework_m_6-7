from decouple import config
from django.contrib import messages
from django.core.mail import send_mail
from django.http import Http404
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, DetailView

from .forms import SubscriberForm, MessageForm, MailingForm
from subscriptions.models import Subscriber, Message, Mailing, MailingAttempt


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


def index(request):
    # Общее количество рассылок
    print("Index view called!")
    total_mailings = Mailing.objects.count()
    print(f"Total mailings: {total_mailings}")

    # Количество активных рассылок (статус 'started')
    active_mailings = Mailing.objects.filter(status='started').count()

    # Количество уникальных получателей (уникальные email)
    unique_subscribers = Subscriber.objects.values('email').distinct().count()

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_subscribers': unique_subscribers,
    }

    return render(request, 'subscriptions/main.html', context)


# Views for Mailing
class MailingListView(ListView):
    model = Mailing
    template_name = 'subscriptions/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        mailings = Mailing.objects.all().prefetch_related('subscribers')
        for mailing in mailings:
            mailing.update_status()
            for subscriber in mailing.subscribers.all():
                subscriber.attempt_count = MailingAttempt.objects.filter(mailing=mailing, subscriber=subscriber).count()

        return mailings



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

    def get_object(self, queryset=None):
        """Override to ensure proper object retrieval"""
        queryset = queryset or self.get_queryset()
        pk = self.kwargs.get('pk')
        if pk is None:
            raise Http404("No primary key specified")

        try:
            obj = get_object_or_404(queryset, pk=pk)
            print(f"Retrieved mailing: ID={obj.id}, PK={obj.pk}")  # Debugging
            return obj
        except Mailing.DoesNotExist:
            raise Http404("Рассылка не найдена")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = self.object
        attempts = MailingAttempt.objects.filter(mailing=mailing)

        attempt_counts = {}
        last_attempts = {}

        for subscriber in mailing.subscribers.all():
            subscriber_attempts = attempts.filter(subscriber=subscriber)
            attempt_counts[subscriber.email] = subscriber_attempts.count()
            last_attempts[subscriber.email] = subscriber_attempts.last() if subscriber_attempts.exists() else None

        context['attempt_counts'] = attempt_counts
        context['last_attempts'] = last_attempts
        return context


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

            successful_sends = 0
            failed_sends = 0

            # Логика отправки сообщений
            for subscriber in mailing.subscribers.all():
                try:
                    send_mail(
                        mailing.message.subject_of_the_letter,
                        mailing.message.letter,
                        config('EMAIL_HOST_USER'),
                        [subscriber.email],
                        fail_silently=False,
                        )

                    MailingAttempt.objects.create(
                        mailing = mailing,
                        subscriber=subscriber,
                        status="successful",
                        server_response="Email sent successfully"
                    )
                    successful_sends += 1

                except Exception as e:
                    MailingAttempt.objects.create(
                        mailing=mailing,
                        status="failed",
                        server_response=str(e)
                    )
                    failed_sends += 1

            messages.success(request, 'Рассылка отправлена!')
        else:
            messages.error(request, 'Рассылка не может быть отправлена до начала!')

        return redirect('subscriptions:mailing_detail', pk=mailing.pk)
