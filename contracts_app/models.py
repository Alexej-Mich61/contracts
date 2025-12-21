# contracts_app/models.py
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords  # ← Для истории


def contract_file_upload_to(instance, filename):
    """Загружает файлы в папку по году: contracts/files/2026/ и т.д."""
    year = timezone.now().year
    return f"contracts/files/{year}/{filename}"


# === ВАЛИДАТОР ФАЙЛОВ ===
def validate_file_size(value):
    if value.size > 20 * 1024 * 1024:  # 20 МБ
        raise ValidationError("Файл не должен превышать 20 МБ.")


# === СПРАВОЧНИКИ ===
class Work(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Название работы")

    class Meta:
        verbose_name = "Работа"
        verbose_name_plural = "Работы"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Название региона")
    code = models.CharField(
        max_length=10, blank=True, null=True, unique=True, verbose_name="Код региона"
    )

    class Meta:
        verbose_name = "Регион"
        verbose_name_plural = "Регионы"
        ordering = ["name"]

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=150, verbose_name="Название района")
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name="districts", verbose_name="Регион"
    )
    population = models.PositiveIntegerField(blank=True, null=True, verbose_name="Население")

    class Meta:
        verbose_name = "Район"
        verbose_name_plural = "Районы"
        unique_together = ("name", "region")
        ordering = ["region__name", "name"]

    def __str__(self):
        return f"{self.name} ({self.region})"


class Implementator(models.Model):
    name = models.CharField(max_length=300, verbose_name="Наименование")
    inn = models.CharField(
        max_length=12,
        unique=True,
        verbose_name="ИНН",
        validators=[RegexValidator(regex=r"^\d{10}$|^\d{12}$", message="ИНН: 10 или 12 цифр.")],
        help_text="10 цифр — юр.лицо, 12 — физ.лицо",
    )

    class Meta:
        verbose_name = "Исполнитель"
        verbose_name_plural = "Исполнители"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (ИНН: {self.inn})"


# === ДОГОВОР ===
class Contract(models.Model):
    STATUS_CHOICES = (
        ("pending", "Ожидание"),  # ← НОВЫЙ СТАТУС
        ("active", "Действует"),
        ("completed", "Завершён"),
    )

    customer_name = models.CharField(max_length=300, verbose_name="Заказчик")
    customer_inn = models.CharField(
        max_length=12,
        verbose_name="ИНН Заказчика",
        validators=[RegexValidator(regex=r"^\d{10}$|^\d{12}$", message="ИНН: 10 или 12 цифр.")],
        help_text="10 цифр — юр.лицо, 12 — физ.лицо",
    )
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    implementator = models.ForeignKey(
        Implementator, on_delete=models.PROTECT, verbose_name="Исполнитель"
    )

    # Чек-лист
    gos_services = models.BooleanField(default=False, verbose_name="Госуслуги")
    oko = models.BooleanField(default=False, verbose_name="ОКО")
    spolokh = models.BooleanField(default=False, verbose_name="Сполох")

    # === ЧЕК-ЛИСТ: СТАДИЯ ПОДПИСАНИЯ ===
    contract_to_be_signed = models.BooleanField(default=True, verbose_name="На подписании")
    contract_signed = models.BooleanField(default=False, verbose_name="Подписан")
    contract_signed_in_trading_platform = models.BooleanField(default=False, verbose_name="Торги")
    contract_signed_in_EDO = models.BooleanField(default=False, verbose_name="ЭДО")
    contract_original_received = models.BooleanField(
        default=False, verbose_name="Бумажный оригинал"
    )
    contract_termination = models.BooleanField(default=False, verbose_name="Расторжение")

    # Примечание
    note = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Примечание",
        help_text="Дополнительная информация (не обязательно)",
    )

    # Работы
    works = models.ManyToManyField(
        Work,
        verbose_name="Работы",
        related_name="contracts",
        help_text="Обязательно для заполнения",
    )

    # СУММА ВСЕГО
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Сумма общая",
        help_text="Например: 55 200.00",
    )

    # СУММА В МЕСЯЦ
    monthly_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Сумма в месяц",
        help_text="Например: 4 600.00",
    )

    # Файлы (1–3) — остаются необязательными

    file1 = models.FileField(
        upload_to=contract_file_upload_to,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf", "doc", "docx", "jpg", "png", "jpeg"]),
            validate_file_size,
        ],
        verbose_name="Файл 1",
    )
    file2 = models.FileField(
        upload_to=contract_file_upload_to,
        blank=True,
        null=True,
        validators=[validate_file_size],
        verbose_name="Файл 2",
    )
    file3 = models.FileField(
        upload_to=contract_file_upload_to,
        blank=True,
        null=True,
        validators=[validate_file_size],
        verbose_name="Файл 3",
    )

    # СТАТУС АВТОМАТИЧЕСКИЙ
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",  # ← теперь по умолчанию "Ожидание"
        editable=False,
        verbose_name="Статус",
    )

    # ФЛАГ ДЛЯ АРХИВА
    is_active = models.BooleanField(default=True, verbose_name="Актуальный")

    # Учёт создания и обновления
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлён")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_contracts",
        verbose_name="Создал",
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_contracts",
        verbose_name="Обновил",
    )

    # История изменений (django-simple-history)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Долгосрочный договор"
        verbose_name_plural = "Долгосрочные договоры"
        ordering = ["-start_date"]

    def __str__(self):
        return f"Договор с {self.customer_name} ({self.start_date} — {self.end_date})"

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Дата начала не может быть позже даты окончания.")

    def save(self, *args, **kwargs):
        today = timezone.now().date()

        # ← УМНАЯ ЛОГИКА СТАТУСА
        if self.start_date and self.end_date:
            if today < self.start_date:
                self.status = "pending"  # ещё не начался
            elif self.start_date <= today <= self.end_date:
                self.status = "active"  # сейчас действует
            else:
                self.status = "completed"  # закончился
        else:
            self.status = "pending"  # если даты не указаны

        # ← ЛОГИКА ДЛЯ ЧЕК-ЛИСТА "СТАДИЯ ПОДПИСАНИЯ": только один пункт стадии подписания может быть True
        signing_fields = [
            "contract_to_be_signed",
            "contract_signed",
            "contract_signed_in_trading_platform",
            "contract_signed_in_EDO",
            "contract_original_received",
            "contract_termination",
        ]

        true_count = sum(getattr(self, field) for field in signing_fields)

        # Если включено больше одного — оставляем только тот, который пользователь выбрал последним
        # (или первый True, если несколько)
        if true_count > 1:
            # Находим первый True и оставляем только его
            for field in signing_fields:
                if getattr(self, field):
                    setattr(self, field, True)
                    break
            # Все остальные — False
            for field in signing_fields[1:]:
                setattr(self, field, False)

        # Если ни один не включён — по умолчанию "На подписании"
        if true_count == 0:
            self.contract_to_be_signed = True
            for field in signing_fields[1:]:
                setattr(self, field, False)

        super().save(*args, **kwargs)

    def file_count(self):
        return sum(bool(getattr(self, f"file{i}", None)) for i in range(1, 4))

    file_count.short_description = "Файлов"


# === АБОНЕНТСКИЙ КОМПЛЕКТ (АК) ===
class AK(models.Model):
    contract = models.ForeignKey(
        "Contract", on_delete=models.CASCADE, related_name="aks", verbose_name="Договор"
    )
    number = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99999999)],
        verbose_name="Номер АК",
        help_text="Макс. 8 цифр",
    )
    district = models.ForeignKey(District, on_delete=models.PROTECT, verbose_name="Район")
    address = models.CharField(max_length=500, verbose_name="Адрес")

    class Meta:
        verbose_name = "Абонентский комплект (АК)"
        verbose_name_plural = "Абонентские комплекты (АК)"
        unique_together = ("contract", "number")
        ordering = ["number"]

    def __str__(self):
        return f"АК {self.number} — {self.address}"
