#contracts_app/admin.py
from django.contrib import admin
from .models import Work, Region, District, Implementator, Contract, AK


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'district_count')
    search_fields = ('name', 'code')
    def district_count(self, obj): return obj.districts.count()
    district_count.short_description = "Районов"


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'population')
    list_filter = ('region',)
    search_fields = ('name', 'region__name')
    list_select_related = ('region',)


@admin.register(Implementator)
class ImplementatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'inn')
    search_fields = ('name', 'inn')


# Инлайн для АК
class AKInline(admin.TabularInline):
    model = AK
    extra = 1
    min_num = 0
    max_num = 500


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'implementator', 'start_date', 'end_date', 'status', 'file_count', 'ak_count')
    list_filter = ('status', 'implementator', 'start_date', 'end_date')
    search_fields = ('customer_name', 'customer_inn', 'implementator__name')
    inlines = [AKInline]
    readonly_fields = ('status', 'created_at', 'updated_at')

    fieldsets = (
        ("Заказчик", {'fields': ('customer_name', 'customer_inn')}),
        ("Сроки", {'fields': ('start_date', 'end_date')}),
        ("Исполнитель", {'fields': ('implementator',)}),
        ("Чек-лист", {'fields': ('gos_services', 'oko', 'spolokh')}),
        ("Файлы", {'fields': ('file1', 'file2', 'file3')}),
        ("Система", {'fields': ('status', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def ak_count(self, obj):
        return obj.aks.count()
    ak_count.short_description = "АК"

    def file_count(self, obj):
        return obj.file_count()
    file_count.short_description = "Файлов"