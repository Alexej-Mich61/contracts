from django import template

register = template.Library()

@register.filter
def get_extension(filename):
    """Возвращает расширение файла в верхнем регистре"""
    if '.' in filename:
        return filename.rsplit('.', 1)[-1].upper()
    return 'FILE'