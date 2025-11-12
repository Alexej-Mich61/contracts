# contracts_app/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models import Q
from .models import Contract
from .forms import ContractForm, AKFormSet


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
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['ak_formset'] = AKFormSet(self.request.POST, self.request.FILES)
        else:
            context['ak_formset'] = AKFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        ak_formset = context['ak_formset']
        if ak_formset.is_valid():
            self.object = form.save()
            ak_formset.instance = self.object
            ak_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class ContractUpdateView(SuccessMessageMixin, UpdateView):
    model = Contract
    form_class = ContractForm
    template_name = 'contracts/contract_form.html'
    success_url = reverse_lazy('contracts:contract_list')
    success_message = "Договор успешно обновлён!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['ak_formset'] = AKFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['ak_formset'] = AKFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        ak_formset = context['ak_formset']
        if ak_formset.is_valid():
            self.object = form.save()
            ak_formset.instance = self.object
            ak_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)