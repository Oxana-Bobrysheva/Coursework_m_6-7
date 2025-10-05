from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages


class ManagerRequiredMixin(UserPassesTestMixin):
    """Mixin для ограничения доступа только менеджерами (группа 'Manager')"""

    def test_func(self):
        return self.request.user.groups.filter(name='Manager').exists()

    def handle_no_permission(self):
        messages.error(self.request, 'Доступ запрещен. Только для менеджеров.')
        return redirect('subscriptions:main')
