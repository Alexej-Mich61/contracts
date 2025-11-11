#contracts_app/admin.py
from django.contrib import admin
from .models import ContractType, Work, Region, District


@admin.register(ContractType)
class ContractTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'work_count')
    search_fields = ('name',)
    ordering = ('name',)

    def work_count(self, obj):
        return obj.works.count()
    work_count.short_description = "Кол-во работ"


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('name', 'contract_type', 'price')
    list_filter = ('contract_type',)
    search_fields = ('name', 'contract_type__name')
    list_select_related = ('contract_type',)  # Оптимизация
    ordering = ('contract_type__name', 'name')

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'district_count')
    search_fields = ('name', 'code')
    ordering = ('name',)

    def district_count(self, obj):
        return obj.districts.count()
    district_count.short_description = "Кол-во районов"


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'population')
    list_filter = ('region',)
    search_fields = ('name', 'region__name')
    list_select_related = ('region',)
    ordering = ('region__name', 'name')