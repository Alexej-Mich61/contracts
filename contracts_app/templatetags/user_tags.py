# contracts_app/templatetags/user_tags.py
from django import template

register = template.Library()

@register.filter
def in_group(user, group_name):
    """Проверяет, состоит ли пользователь в группе с именем group_name"""
    return user.groups.filter(name=group_name).exists()