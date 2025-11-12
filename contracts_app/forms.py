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
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end and start > end:
            raise ValidationError("Дата начала не может быть позже даты окончания.")

        files = [cleaned_data.get(f'file{i}') for i in range(1, 4)]
        if not any(f for f in files if f):
            raise ValidationError("Прикрепите хотя бы один файл.")
        return cleaned_data


class AKForm(forms.ModelForm):
    class Meta:
        model = AK
        fields = ['number', 'district', 'address']


AKFormSet = inlineformset_factory(
    Contract, AK,
    form=AKForm,
    extra=1,
    can_delete=True,
    min_num=0,
    max_num=500,
    validate_max=True
)