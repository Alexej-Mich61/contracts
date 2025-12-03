# contracts_app/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from .models import Contract, Implementator, Work
from .forms import ContractForm, AKFormSet




def contract_list(request):
    # Базовый запрос
    contracts = Contract.objects.select_related('implementator') \
        .prefetch_related('aks', 'works') \
        .annotate(ak_count=Count('aks')) \
        .order_by('-id')

    implementators = Implementator.objects.all().order_by('name')
    all_works = Work.objects.all().order_by('name')

    # === ФИЛЬТРАЦИЯ ===
    if request.GET:
        # 1. Поиск по заказчику / ИНН — 100% регистронезависимый
        if q := request.GET.get('q'):
            contracts = contracts.filter(
                Q(customer_name__icontains=q) | Q(customer_inn__icontains=q)
            )

        # 2. Номер АК
        if ak_number := request.GET.get('ak_number'):
            contracts = contracts.filter(aks__number=ak_number)

        # 3. Район АК — регистронезависимый
        if ak_district := request.GET.get('ak_district'):
            contracts = contracts.filter(aks__district__name__icontains=ak_district.strip())

        # 4. Адрес АК — регистронезависимый
        if ak_address := request.GET.get('ak_address'):
            contracts = contracts.filter(aks__address__icontains=ak_address.strip())

        # 5. Статус
        if status := request.GET.get('status'):
            contracts = contracts.filter(status=status)

        # 6. Исполнитель
        if impl := request.GET.get('implementator'):
            contracts = contracts.filter(implementator_id=impl)

        # 7. Работы (множественный)
        if works := request.GET.getlist('works'):
            contracts = contracts.filter(works__pk__in=works)

        # 8. Чек-лист (хотя бы один включён)
        checklist_filters = Q()
        if request.GET.get('gos_services'):
            checklist_filters |= Q(gos_services=True)
        if request.GET.get('oko'):
            checklist_filters |= Q(oko=True)
        if request.GET.get('spolokh'):
            checklist_filters |= Q(spolokh=True)
        if checklist_filters:
            contracts = contracts.filter(checklist_filters)

        # Убираем дубли из-за join
        contracts = contracts.distinct()

    # ПАГИНАЦИЯ — 10 записей на страницу
    paginator = Paginator(contracts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,  # ← теперь передаём page_obj, а не contracts
        'contracts': page_obj,  # ← оставляем для совместимости с шаблоном
        'implementators': implementators,
        'all_works': all_works,
        'is_paginated': page_obj.has_other_pages(),  # для красоты
    }
    return render(request, 'contracts/contract_list.html', context)



class ContractDetailView(DetailView):
    model = Contract
    template_name = 'contracts/contract_detail.html'
    context_object_name = 'contract'

class ContractCreateView(SuccessMessageMixin, CreateView):
    model = Contract
    form_class = ContractForm
    template_name = 'contracts/contract_form.html'
    success_url = reverse_lazy('contracts:contract_list')
    success_message = "Договор успешно создан!"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['ak_formset'] = AKFormSet(self.request.POST, self.request.FILES)
        else:
            data['ak_formset'] = AKFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        ak_formset = context['ak_formset']

        # Сохраняем контракт
        self.object = form.save()

        # Привязываем формсет к сохранённому объекту
        ak_formset.instance = self.object
        if ak_formset.is_valid():
            ak_formset.save()
        else:
            # Если АК невалидны — возвращаем форму с ошибками
            return self.form_invalid(form)

        return super().form_valid(form)

    def form_invalid(self, form):
        # Добавляем формсет в контекст, чтобы ошибки отобразились
        context = self.get_context_data()
        context['ak_formset'] = AKFormSet(self.request.POST, self.request.FILES)
        return self.render_to_response(context)


class ContractUpdateView(SuccessMessageMixin, UpdateView):
    model = Contract
    form_class = ContractForm
    template_name = 'contracts/contract_form.html'
    success_url = reverse_lazy('contracts:contract_list')
    success_message = "Договор успешно обновлён!"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['ak_formset'] = AKFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['ak_formset'] = AKFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        ak_formset = context['ak_formset']
        self.object = form.save()
        ak_formset.instance = self.object
        if ak_formset.is_valid():
            ak_formset.save()
        else:
            return self.form_invalid(form)
        return super().form_valid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        context['ak_formset'] = AKFormSet(self.request.POST, self.request.FILES, instance=self.object)
        return self.render_to_response(context)

class ContractDeleteView(SuccessMessageMixin, DeleteView):
    model = Contract
    success_url = reverse_lazy('contracts:contract_list')
    success_message = "Договор успешно удалён."

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


@require_POST
def update_checklist(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    contract.gos_services = 'gos_services' in request.POST
    contract.oko = 'oko' in request.POST
    contract.spolokh = 'spolokh' in request.POST
    contract.save()
    return JsonResponse({'success': True, 'message': 'Чек-лист обновлён'})