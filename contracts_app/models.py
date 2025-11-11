# contracts_app/models.py
from django.db import models
from django.core.exceptions import ValidationError


class ContractType(models.Model):
    """Справочник: Тип договора"""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Название типа договора"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )

    class Meta:
        verbose_name = "Тип договора"
        verbose_name_plural = "Типы договоров"
        ordering = ['name']

    def __str__(self):
        return self.name


class Work(models.Model):
    """Справочник: Работы, привязанные к типу договора"""
    name = models.CharField(
        max_length=200,
        verbose_name="Название работы"
    )
    contract_type = models.ForeignKey(
        ContractType,
        on_delete=models.CASCADE,
        related_name='works',
        verbose_name="Тип договора"
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True, null=True,
        verbose_name="Стоимость (по умолчанию)"
    )

    class Meta:
        verbose_name = "Работа"
        verbose_name_plural = "Работы"
        unique_together = ('name', 'contract_type')  # Одна работа на тип
        ordering = ['contract_type__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.contract_type})"


class Region(models.Model):
    """Справочник: Регион"""
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Название региона"
    )
    code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Код региона (ISO, почтовый и т.п.)"
    )

    class Meta:
        verbose_name = "Регион"
        verbose_name_plural = "Регионы"
        ordering = ['name']

    def __str__(self):
        return self.name


class District(models.Model):
    """Справочник: Район, привязанный к региону"""
    name = models.CharField(
        max_length=150,
        verbose_name="Название района"
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='districts',
        verbose_name="Регион"
    )
    population = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Население"
    )

    class Meta:
        verbose_name = "Район"
        verbose_name_plural = "Районы"
        unique_together = ('name', 'region')  # Один район в регионе
        ordering = ['region__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.region})"