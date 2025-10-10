from django import forms
from django.utils import timezone

from .models import Subscriber, Message, Mailing


class SubscriberForm(forms.ModelForm):
    """Эта форма будет использоваться для добавления нового подписчика."""
    class Meta:
        model = Subscriber
        fields = ['email', 'name', 'comment']
        labels = {
            'email': 'Укажите почту',
            'name': 'Имя подписчика',
            'comment': 'Комментарии о подписчике'
            }


class MessageForm(forms.ModelForm):
    """Эта форма будет использоваться для добавления нового подписчика."""
    class Meta:
        model = Message
        fields = ['subject_of_the_letter', 'letter']
        labels = {
            'subject_of_the_letter': 'Укажите тему письма',
            'letter': 'Содержание вашего письма',
            }


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['start_time', 'end_time', 'message', 'subscribers']
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'end_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'message': forms.Select(attrs={'class': 'form-control'}),
            'subscribers': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
        labels = {
            'start_time': 'Дата и время начала',
            'end_time': 'Дата и время окончания',
            'message': 'Сообщение',
            'subscribers': 'Получатели',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            # Фильтруем подписчиков по owner
            self.fields['subscribers'].queryset = Subscriber.objects.filter(owner=self.user)

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError("Время окончания должно быть позже времени начала!")

        return cleaned_data
