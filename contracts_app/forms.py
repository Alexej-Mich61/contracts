# contracts_app/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Contract, AK
from django.forms import inlineformset_factory


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = [
            'customer_name', 'customer_inn',
            'start_date', 'end_date',
            'implementator',
            'gos_services', 'oko', 'spolokh',
            'file1', 'file2', 'file3'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'gos_services': forms.CheckboxInput(),
            'oko': forms.CheckboxInput(),
            'spolokh': forms.CheckboxInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise ValidationError("Дата начала не может быть позже даты окончания.")

        # Проверка: хотя бы 1 файл
        files = [cleaned_data.get(f'file{i}') for i in range(1, 4)]
        if not any(files):
            raise ValidationError("Прикрепите хотя бы один файл.")

        return cleaned_data


class AKForm(forms.ModelForm):
    class Meta:
        model = AK
        fields = ['number', 'district', 'address']
        widgets = {
            'district': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['number'].widget.attrs.update({'class': 'form-control', 'min': '1', 'max': '99999999'})
        self.fields['district'].empty_label = "— Выберите район —"


# Формсет для АК
AKFormSet = inlineformset_factory(
    Contract, AK,
    form=AKForm,
    extra=1,
    can_delete=True,
    min_num=0,
    max_num=500,
    validate_min=False,
    validate_max=True
)