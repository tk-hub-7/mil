from django.contrib import admin
from .models import (
    Base, EquipmentType, Inventory, Purchase, Transfer,
    Assignment, Expenditure, UserRole, RoleCode, APILog
)


@admin.register(Base)
class BaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'location', 'created_at', 'is_deleted']
    list_filter = ['is_deleted', 'created_at']
    search_fields = ['name', 'code', 'location']


@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit', 'created_at', 'is_deleted']
    list_filter = ['is_deleted', 'created_at']
    search_fields = ['name', 'description']


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['base', 'equipment_type', 'quantity', 'updated_at']
    list_filter = ['base', 'equipment_type']
    search_fields = ['base__name', 'equipment_type__name']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['base', 'equipment_type', 'quantity', 'supplier', 'purchase_date', 'created_by']
    list_filter = ['base', 'equipment_type', 'purchase_date', 'is_deleted']
    search_fields = ['supplier', 'base__name', 'equipment_type__name']
    date_hierarchy = 'purchase_date'


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ['from_base', 'to_base', 'equipment_type', 'quantity', 'status', 'transfer_date']
    list_filter = ['status', 'from_base', 'to_base', 'transfer_date', 'is_deleted']
    search_fields = ['from_base__name', 'to_base__name', 'equipment_type__name']
    date_hierarchy = 'transfer_date'


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['base', 'equipment_type', 'personnel_name', 'assigned_quantity', 'returned_quantity', 'assignment_date']
    list_filter = ['base', 'equipment_type', 'assignment_date', 'is_deleted']
    search_fields = ['personnel_name', 'personnel_id', 'base__name', 'equipment_type__name']
    date_hierarchy = 'assignment_date'


@admin.register(Expenditure)
class ExpenditureAdmin(admin.ModelAdmin):
    list_display = ['base', 'equipment_type', 'quantity', 'expenditure_date', 'created_by']
    list_filter = ['base', 'equipment_type', 'expenditure_date', 'is_deleted']
    search_fields = ['reason', 'base__name', 'equipment_type__name']
    date_hierarchy = 'expenditure_date'


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'assigned_base', 'created_at']
    list_filter = ['role', 'assigned_base']
    search_fields = ['user__username', 'user__email']


@admin.register(RoleCode)
class RoleCodeAdmin(admin.ModelAdmin):
    list_display = ['role', 'code', 'is_active', 'created_at']
    list_filter = ['role', 'is_active']
    search_fields = ['code', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(APILog)
class APILogAdmin(admin.ModelAdmin):
    list_display = ['user', 'method', 'endpoint', 'status_code', 'timestamp']
    list_filter = ['method', 'status_code', 'timestamp']
    search_fields = ['endpoint', 'user__username']
    date_hierarchy = 'timestamp'
    readonly_fields = ['user', 'endpoint', 'method', 'status_code', 'request_body', 'response_body', 'ip_address', 'timestamp']
