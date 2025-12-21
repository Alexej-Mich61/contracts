# contracts_app/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from .forms import AKFormSet, ContractForm
from .models import Contract
from .permissions import ViewOnlyPermissionMixin
from .services import (
    export_contracts_to_excel,
    get_contract_list_context,
    update_contract_signing_stage,
)


def custom_page_not_found(request, exception):
    return render(request, "404.html", status=404)


def permission_denied_view(request, exception=None):
    return render(request, "403.html", status=403)


def custom_server_error(request):
    return render(request, "500.html", status=500)


@require_POST
@login_required
def update_signing_stage(request, pk):
    stage = request.POST.get("signing_stage")
    return update_contract_signing_stage(request.user, pk, stage)


@login_required
def contract_list(request):
    context = get_contract_list_context(request)
    return render(request, "contracts/contract_list.html", context)


@login_required
def export_contracts_excel(request):
    return export_contracts_to_excel(request.GET)


class ContractDetailView(DetailView):
    model = Contract
    template_name = "contracts/contract_detail.html"
    context_object_name = "contract"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["historical"] = self.object.history.all().order_by("-history_date")
        return context


class ContractCreateView(ViewOnlyPermissionMixin, CreateView):
    model = Contract
    form_class = ContractForm
    template_name = "contracts/contract_form.html"
    success_url = reverse_lazy("contracts:contract_list")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["ak_formset"] = AKFormSet(self.request.POST, self.request.FILES)
        else:
            data["ak_formset"] = AKFormSet()
        return data

    def form_valid(self, form):
        # Присваиваем пользователя ДО сохранения
        if self.request.user.is_authenticated:
            if not self.object:  # Создание (object ещё не существует)
                form.instance.created_by = self.request.user
            form.instance.updated_by = self.request.user

        # Стандартное сохранение формы (создаёт/обновляет объект)
        response = super().form_valid(form)

        # Теперь object существует — сохраняем формсет АК
        ak_formset = AKFormSet(self.request.POST, self.request.FILES, instance=self.object)
        if ak_formset.is_valid():
            ak_formset.save()

        # Добавляем сообщение в сессию
        messages.success(
            self.request,
            "Договор успешно создан!" if not self.object.pk else "Договор успешно обновлён!",
        )
        return response

    def form_invalid(self, form):
        # Добавляем формсет в контекст, чтобы ошибки отобразились
        context = self.get_context_data()
        context["ak_formset"] = AKFormSet(self.request.POST, self.request.FILES)
        return self.render_to_response(context)


class ContractUpdateView(ViewOnlyPermissionMixin, UpdateView):
    model = Contract
    form_class = ContractForm
    template_name = "contracts/contract_form.html"
    success_url = reverse_lazy("contracts:contract_list")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["ak_formset"] = AKFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            data["ak_formset"] = AKFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        # Присваиваем пользователя ДО сохранения
        if self.request.user.is_authenticated:
            form.instance.updated_by = self.request.user

        # Стандартное сохранение
        response = super().form_valid(form)

        # Сохраняем формсет АК
        ak_formset = AKFormSet(self.request.POST, self.request.FILES, instance=self.object)
        if ak_formset.is_valid():
            ak_formset.save()

        messages.success(self.request, "Договор успешно обновлён!")
        return response

    def form_invalid(self, form):
        context = self.get_context_data()
        context["ak_formset"] = AKFormSet(
            self.request.POST, self.request.FILES, instance=self.object
        )
        return self.render_to_response(context)


class ContractDeleteView(ViewOnlyPermissionMixin, DeleteView):
    model = Contract
    success_url = reverse_lazy("contracts:contract_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Договор успешно удалён.")
        return super().delete(request, *args, **kwargs)


@require_POST
def update_checklist(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    contract.gos_services = "gos_services" in request.POST
    contract.oko = "oko" in request.POST
    contract.spolokh = "spolokh" in request.POST
    contract.save()
    return JsonResponse({"success": True, "message": "Чек-лист обновлён"})
