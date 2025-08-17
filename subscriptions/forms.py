from django import forms
from .models import Subscriber, Message


class SubscriberForm(forms.ModelForm):
    """Эта форма будет использоваться для добавления нового подписчика."""
    class Meta:
        model = Subscriber
        fields = ['email', 'name', 'comment']


class MessageForm(forms.ModelForm):
    """Эта форма будет использоваться для добавления нового подписчика."""
    class Meta:
        model = Message
        fields = ['subject_of_the_letter', 'letter']