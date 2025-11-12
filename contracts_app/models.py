#contracts_app/models.py
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.utils import timezone
from django.core.exceptions import ValidationError


# === СПРАВОЧНИКИ ===
class Work(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Название работы")
    class Meta:
        verbose_name = "Работа"
        verbose_name_plural = "Работы"
        ordering = ['name']
    def __str__(self): return self.name


class Region(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Название региона")
    code = models.CharField(max_length=10, blank=True, null=True, unique=True, verbose_name="Код региона")
    class Meta:
        verbose_name = "Регион"
        verbose_name_plural = "Регионы"
        ordering = ['name']
    def __str__(self): return self.name


class District(models.Model):
    name = models.CharField(max_length=150, verbose_name="Название района")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='districts', verbose_name="Регион")
    population = models.PositiveIntegerField(blank=True, null=True, verbose_name="Население")
    class Meta:
        verbose_name = "Район"
        verbose_name_plural = "Районы"
        unique_together = ('name', 'region')
        ordering = ['region__name', 'name']
    def __str__(self): return f"{self.name} ({self.region})"


class Implementator(models.Model):
    name = models.CharField(max_length=300, verbose_name="Наименование")
    inn = models.CharField(
        max_length=12, unique=True, verbose_name="ИНН",
        validators=[RegexValidator(regex=r'^\d{10}$|^\d{12}$', message="ИНН: 10 или 12 цифр.")],
        help_text="10 цифр — юр.лицо, 12 — физ.лицо"
    )
    class Meta:
        verbose_name = "Исполнитель"
        verbose_name_plural = "Исполнители"
        ordering = ['name']
    def __str__(self): return f"{self.name} (ИНН: {self.inn})"


# === ДОГОВОР ===
def validate_file_size(value):
    if value.size > 20 * 1024 * 1024:  # 20 МБ
        raise ValidationError("Файл не должен превышать 20 МБ.")


class Contract(models.Model):
    STATUS_CHOICES = (
        ('active', 'Действует'),
        ('completed', 'Завершён'),
    )

    customer_name = models.CharField(max_length=300, verbose_name="Заказчик")
    customer_inn = models.CharField(
        max_length=12, verbose_name="ИНН Заказчика",
        validators=[RegexValidator(regex=r'^\d{10}$|^\d{12}$', message="ИНН: 10 или 12 цифр.")],
        help_text="10 цифр — юр.лицо, 12 — физ.лицо"
    )
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    implementator = models.ForeignKey(Implementator, on_delete=models.PROTECT, verbose_name="Исполнитель")

    # Чек-лист
    gos_services = models.BooleanField(default=False, verbose_name="Госуслуги")
    oko = models.BooleanField(default=False, verbose_name="ОКО")
    spolokh = models.BooleanField(default=False, verbose_name="Сполох")

    # Файлы (1–3)
    file1 = models.FileField(
        upload_to='contracts/files/', blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'png', 'jpeg']), validate_file_size],
        verbose_name="Файл 1"
    )
    file2 = models.FileField(upload_to='contracts/files/', blank=True, null=True, validators=[validate_file_size], verbose_name="Файл 2")
    file3 = models.FileField(upload_to='contracts/files/', blank=True, null=True, validators=[validate_file_size], verbose_name="Файл 3")

    # Автостатус
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, editable=False, verbose_name="Статус")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлён")

    class Meta:
        verbose_name = "Долгосрочный договор"
        verbose_name_plural = "Долгосрочные договоры"
        ordering = ['-start_date']

    def __str__(self):
        return f"Договор с {self.customer_name} ({self.start_date} — {self.end_date})"

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Дата начала не может быть позже даты окончания.")

    def save(self, *args, **kwargs):
        # Автостатус
        today = timezone.now().date()
        if self.end_date and today > self.end_date:
            self.status = 'completed'
        else:
            self.status = 'active'
        super().save(*args, **kwargs)

    def file_count(self):
        return sum(1 for f in [self.file1, self.file2, self.file3] if f)
    file_count.short_description = "Файлов"


# === АБОНЕНТСКИЙ КОМПЛЕКТ (АК) ===
class AK(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='aks', verbose_name="Договор")
    number = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99999999)],
        verbose_name="Номер АК",
        help_text="Макс. 8 цифр"
    )
    district = models.ForeignKey(District, on_delete=models.PROTECT, verbose_name="Район")
    address = models.CharField(max_length=500, verbose_name="Адрес")

    class Meta:
        verbose_name = "Абонентский комплект (АК)"
        verbose_name_plural = "Абонентские комплекты (АК)"
        unique_together = ('contract', 'number')  # Уникальный номер в договоре
        ordering = ['number']

    def __str__(self):
        return f"АК {self.number} — {self.address}"