from decouple import config
from django.contrib import messages
from django.core.mail import send_mail
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, DetailView
from django.contrib.auth.models import Group, User
from .mixins import ManagerRequiredMixin
from django.db.models import Count, Prefetch

from .forms import SubscriberForm, MessageForm, MailingForm
from subscriptions.models import Subscriber, Message, Mailing, MailingAttempt


def is_manager(user):
    return user.groups.filter(name='Manager').exists()


def mailing_toggle_active(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    if is_manager(request.user):
        mailing.is_active = not mailing.is_active
        mailing.save()
        messages.success(request, f'Рассылка {"деактивирована" if not mailing.is_active else "активирована"}.')
    return redirect('subscriptions:mailing_list')


# All views for Subscriber
class SubscriberCreateView(LoginRequiredMixin, CreateView):
    model = Subscriber
    form_class = SubscriberForm
    template_name = 'subscriptions/subscribe.html'
    success_url = reverse_lazy('subscriptions:subscribers_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class SubscriberListView(LoginRequiredMixin, ListView):
    model = Subscriber
    template_name = "subscriptions/subscribers_list.html"
    context_object_name = 'subscribers'

    def get_queryset(self):
        user = self.request.user
        if is_manager(user):
            return Subscriber.objects.all()
        return Subscriber.objects.filter(owner=user)


class SubscriberUpdateView(LoginRequiredMixin, UpdateView):
    model = Subscriber
    form_class = SubscriberForm
    template_name = 'subscriptions/subscribe.html'
    success_url = reverse_lazy('subscriptions:subscribers_list')

    def get_queryset(self):
        user = self.request.user
        if is_manager(user):
            return Subscriber.objects.all()
        return Subscriber.objects.filter(owner=user)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not is_manager(request.user) and obj.owner != request.user:
            messages.error(request, 'У вас нет прав для редактирования этого клиента.')
            return redirect('subscriptions:subscribers_list')
        return super().dispatch(request, *args, **kwargs)


class SubscriberDeleteView(LoginRequiredMixin, DeleteView):
    model = Subscriber
    template_name = "subscriptions/subscriber_confirm_delete.html"
    success_url = reverse_lazy("subscriptions:subscribers_list")

    def get_queryset(self):
        user = self.request.user
        if is_manager(user):
            return Subscriber.objects.all()
        return Subscriber.objects.filter(owner=user)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not is_manager(request.user) and obj.owner != request.user:
            messages.error(request, 'У вас нет прав для удаления этого клиента.')
            return redirect('subscriptions:subscribers_list')
        return super().dispatch(request, *args, **kwargs)


# All views for Message
class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'subscriptions/message.html'
    success_url = reverse_lazy('subscriptions:messages_list')


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "subscriptions/messages_list.html"
    context_object_name = 'messages'


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'subscriptions/message.html'
    success_url = reverse_lazy('subscriptions:messages_list')


class MessageDeleteView(LoginRequiredMixin, DeleteView):
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


@cache_page(60 * 15)
def index(request):
    user = request.user
    print("Index view called!")

    # Инициализация переменных по умолчанию
    total_mailings = 0
    active_mailings = 0
    unique_subscribers = 0

    if user.is_authenticated:
        # Фильтрация по owner только для аутентифицированных пользователей
        if is_manager(user):
            total_mailings = Mailing.objects.count()
            active_mailings = Mailing.objects.filter(status='started').count()
            unique_subscribers = Subscriber.objects.values('email').distinct().count()
        else:
            total_mailings = Mailing.objects.filter(owner=user).count()
            active_mailings = Mailing.objects.filter(owner=user, status='started').count()
            unique_subscribers = Subscriber.objects.filter(owner=user).values('email').distinct().count()
    else:
        total_mailings = Mailing.objects.count()
        active_mailings = Mailing.objects.filter(status='started').count()
        unique_subscribers = Subscriber.objects.values('email').distinct().count()
    print(f"Total mailings: {total_mailings}")
    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_subscribers': unique_subscribers,
    }
    return render(request, 'subscriptions/main.html', context)


# Views for Mailing
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'subscriptions/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        user = self.request.user
        if is_manager(user):
            # Менеджеры видят все рассылки
            queryset = Mailing.objects.all()
        else:
            # Пользователи видят только свои рассылки
            queryset = Mailing.objects.filter(owner=user)

        # Оптимизация: prefetch_related для subscribers и message, select_related для owner
        queryset = queryset.select_related('owner', 'message').prefetch_related(
            Prefetch('subscribers', queryset=Subscriber.objects.annotate(
                attempt_count=Count('mailingattempt')  # Подсчитываем попытки для каждого subscriber
            ))
        )

        for mailing in queryset:
            mailing.update_status()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'subscriptions/mailing_form.html'
    success_url = reverse_lazy('subscriptions:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'subscriptions/mailing_form.html'
    success_url = reverse_lazy('subscriptions:mailing_list')

    def get_queryset(self):
        user = self.request.user
        if is_manager(user):
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not is_manager(request.user) and obj.owner != request.user:
            messages.error(request, 'У вас нет прав для редактирования этой рассылки.')
            return redirect('subscriptions:mailing_list')
        return super().dispatch(request, *args, **kwargs)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'subscriptions/mailing_confirm_delete.html'
    success_url = reverse_lazy('subscriptions:mailing_list')

    def get_queryset(self):
        user = self.request.user
        if is_manager(user):
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not is_manager(request.user) and obj.owner != request.user:
            messages.error(request, 'У вас нет прав для удаления этой рассылки.')
            return redirect('subscriptions:mailing_list')
        return super().dispatch(request, *args, **kwargs)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'subscriptions/mailing_detail.html'
    context_object_name = 'mailing'

    def get_queryset(self):
        user = self.request.user
        if is_manager(user):
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not is_manager(request.user) and obj.owner != request.user:
            messages.error(request, 'У вас нет прав для просмотра этой рассылки.')
            return redirect('subscriptions:mailing_list')
        return super().dispatch(request, *args, **kwargs)

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


class SendMailingView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        mailing = get_object_or_404(Mailing, pk=kwargs['pk'])
        if not is_manager(request.user) and mailing.owner != request.user:
            messages.error(request, 'У вас нет прав для отправки этой рассылки.')
            return redirect('subscriptions:mailing_list')
        return super().dispatch(request, *args, **kwargs)

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
                        mailing=mailing,
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


class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = 'subscriptions/mailing_attempts.html'
    context_object_name = 'attempts'
    paginate_by = 50

    def get_queryset(self):
        user = self.request.user
        queryset = MailingAttempt.objects.select_related('mailing', 'subscriber')
        if not is_manager(user):
            queryset = queryset.filter(mailing__owner=user)
        mailing_id = self.request.GET.get('mailing')
        if mailing_id:
            queryset = queryset.filter(mailing_id=mailing_id)
        return queryset.order_by('-attempt_time')


class MailingStatsView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'subscriptions/mailing_stats.html'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        mailings = Mailing.objects.filter(owner=user)
        context['total_mailings'] = mailings.count()
        context['active_mailings'] = mailings.filter(is_active=True).count()
        context['completed_mailings'] = mailings.filter(status='completed').count()

        return context


class UserListView(ManagerRequiredMixin, ListView):
    """Список всех пользователей (только для менеджеров)"""
    model = User
    template_name = 'subscriptions/user_list.html'
    context_object_name = 'users'
    paginate_by = 20  # Для больших списков


class UserToggleActiveView(ManagerRequiredMixin, View):
    """Блокировка/разблокировка пользователя (только для менеджеров)"""

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()
        status = "заблокирован" if not user.is_active else "разблокирован"
        messages.success(request, f'Пользователь {user.username} {status}!')
        return redirect('subscriptions:user_list')


class MailingToggleActiveView(ManagerRequiredMixin, View):
    """Отключение/включение рассылки (только для менеджеров)"""

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.is_active = not mailing.is_active
        mailing.save()
        status = "отключена" if not mailing.is_active else "включена"
        messages.success(request, f'Рассылка #{mailing.id} {status}!')
        return redirect('subscriptions:mailing_list')
