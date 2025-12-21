# contracts_app/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from .models import AK, Contract, District


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = [
            "customer_name",
            "customer_inn",
            "start_date",
            "end_date",
            "implementator",
            "gos_services",
            "oko",
            "spolokh",
            "works",
            "total_amount",
            "monthly_amount",
            "note",
            "file1",
            "file2",
            "file3",
            # ← НОВЫЕ ПОЛЯ
            "contract_to_be_signed",
            "contract_signed",
            "contract_signed_in_trading_platform",
            "contract_signed_in_EDO",
            "contract_original_received",
            "contract_termination",
        ]
        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}, format="%Y-%m-%d"  # ← Это важно!
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}, format="%Y-%m-%d"
            ),
            "note": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "works": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Принудительно ставим правильный формат и значение
        self.fields["start_date"].input_formats = ["%Y-%m-%d"]
        self.fields["end_date"].input_formats = ["%Y-%m-%d"]

        if self.instance and self.instance.pk:
            if self.instance.start_date:
                date_str = self.instance.start_date.strftime("%Y-%m-%d")
                self.fields["start_date"].widget.attrs["value"] = date_str
                # Принудительно задаём initial (crispy-forms читает отсюда)
                self.initial["start_date"] = date_str

            if self.instance.end_date:
                date_str = self.instance.end_date.strftime("%Y-%m-%d")
                self.fields["end_date"].widget.attrs["value"] = date_str
                self.initial["end_date"] = date_str

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")
        if start and end and start > end:
            raise ValidationError("Дата начала не может быть позже даты окончания.")
        return cleaned_data


class AKForm(forms.ModelForm):
    class Meta:
        model = AK
        fields = ["number", "district", "address"]
        widgets = {
            "district": forms.Select(attrs={"class": "form-select"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "number": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["district"].queryset = District.objects.select_related("region").order_by(
            "region__name", "name"
        )
        self.fields["district"].label_from_instance = lambda obj: f"{obj.name} — {obj.region.name}"


# Формсет для АК
AKFormSet = inlineformset_factory(
    Contract,
    AK,
    form=AKForm,
    fields=("number", "district", "address"),
    extra=1,
    can_delete=True,
    can_delete_extra=True,
    min_num=0,
    max_num=500,
    validate_max=True,
)
