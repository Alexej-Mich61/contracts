# contracts_app/permissions.py
from django.contrib.auth.mixins import UserPassesTestMixin


class ViewOnlyPermissionMixin(UserPassesTestMixin):
    """
    Разрешает доступ только пользователям с правом "Просмотр",
    но блокирует редактирование/удаление для всех, кроме админов
    """

    def test_func(self):
        user = self.request.user

        # Администраторы могут всё
        if user.is_superuser or user.groups.filter(name='Administrators').exists():
            return True

        # Viewers могут только смотреть (но не редактировать/удалять)
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return user.has_perm('contracts_app.view_contract')

        # Для POST/PUT/DELETE — только админы
        return False