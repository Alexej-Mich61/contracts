# contracts_app/urls.py
from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = "contracts"

urlpatterns = [
    path("", login_required(views.contract_list), name="contract_list"),
    path(
        "contract/<int:pk>/",
        login_required(views.ContractDetailView.as_view()),
        name="contract_detail",
    ),
    path("contract/add/", login_required(views.ContractCreateView.as_view()), name="contract_add"),
    path(
        "contract/<int:pk>/edit/",
        login_required(views.ContractUpdateView.as_view()),
        name="contract_edit",
    ),
    path(
        "contract/<int:pk>/update-checklist/",
        login_required(views.update_checklist),
        name="update_checklist",
    ),
    path(
        "contract/<int:pk>/delete/",
        login_required(views.ContractDeleteView.as_view()),
        name="contract_delete",
    ),
    path("export-excel/", login_required(views.export_contracts_excel), name="export_excel"),
    path(
        "contract/<int:pk>/update-signing-stage/",
        login_required(views.update_signing_stage),
        name="update_signing_stage",
    ),
]
