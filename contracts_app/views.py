# contracts_app/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models import Q
from .models import Contract
from .forms import ContractForm, AKFormSet
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


class ContractListView(ListView):
    model = Contract
    template_name = 'contracts/contract_list.html'
    context_object_name = 'contracts'
    paginate_by = 10
    ordering = ['-start_date']

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        status = self.request.GET.get('status')

        if query:
            queryset = queryset.filter(
                Q(customer_name__icontains=query) |
                Q(customer_inn__icontains=query) |
                Q(implementator__name__icontains=query)
            )
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_status'] = self.request.GET.get('status', '')
        return context


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
    messages.success(request, f"Чек-лист обновлён для договора «{contract.customer_name}»")
    return redirect('contracts:contract_list')