from django import forms
from .models import Subscriber


class SubscriberForm(forms.ModelForm):
    """Эта форма будет использоваться для добавления нового подписчика."""
    class Meta:
        model = Subscriber
        fields = ['email', 'name', 'comment']
