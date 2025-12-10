from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Base, EquipmentType, Inventory, Purchase, Transfer,
    Assignment, Expenditure, UserRole
)


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    assigned_base = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'assigned_base']
        
    def get_role(self, obj):
        try:
            return {
                'role': obj.role.role,
                'role_display': obj.role.get_role_display()
            }
        except UserRole.DoesNotExist:
            return None
            
    def get_assigned_base(self, obj):
        try:
            if obj.role.assigned_base:
                return {
                    'id': obj.role.assigned_base.id,
                    'name': obj.role.assigned_base.name,
                    'code': obj.role.assigned_base.code
                }
        except UserRole.DoesNotExist:
            pass
        return None


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=UserRole.ROLE_CHOICES)
    assigned_base_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role', 'assigned_base_id']
    

        
    def create(self, validated_data):
        role = validated_data.pop('role')
        assigned_base_id = validated_data.pop('assigned_base_id', None)
        
        user = User.objects.create_user(**validated_data)
        
        assigned_base = None
        if assigned_base_id:
            assigned_base = Base.objects.get(id=assigned_base_id)
            
        UserRole.objects.create(
            user=user,
            role=role,
            assigned_base=assigned_base
        )
        
        return user


class BaseSerializer(serializers.ModelSerializer):
    inventory_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Base
        fields = ['id', 'name', 'location', 'code', 'inventory_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        
    def get_inventory_count(self, obj):
        return obj.inventory.filter(quantity__gt=0).count()


class EquipmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentType
        fields = ['id', 'name', 'description', 'unit', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class InventorySerializer(serializers.ModelSerializer):
    base_name = serializers.CharField(source='base.name', read_only=True)
    base_code = serializers.CharField(source='base.code', read_only=True)
    equipment_name = serializers.CharField(source='equipment_type.name', read_only=True)
    equipment_unit = serializers.CharField(source='equipment_type.unit', read_only=True)
    
    class Meta:
        model = Inventory
        fields = [
            'id', 'base', 'base_name', 'base_code',
            'equipment_type', 'equipment_name', 'equipment_unit',
            'quantity', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PurchaseSerializer(serializers.ModelSerializer):
    base_name = serializers.CharField(source='base.name', read_only=True)
    equipment_name = serializers.CharField(source='equipment_type.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Purchase
        fields = [
            'id', 'base', 'base_name', 'equipment_type', 'equipment_name',
            'quantity', 'supplier', 'purchase_date',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        purchase = super().create(validated_data)
        
        # Update inventory
        inventory, created = Inventory.objects.get_or_create(
            base=purchase.base,
            equipment_type=purchase.equipment_type,
            defaults={'quantity': 0}
        )
        inventory.quantity += purchase.quantity
        inventory.save()
        
        return purchase


class TransferSerializer(serializers.ModelSerializer):
    from_base_name = serializers.CharField(source='from_base.name', read_only=True)
    to_base_name = serializers.CharField(source='to_base.name', read_only=True)
    equipment_name = serializers.CharField(source='equipment_type.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Transfer
        fields = [
            'id', 'from_base', 'from_base_name', 'to_base', 'to_base_name',
            'equipment_type', 'equipment_name', 'quantity', 'status', 'transfer_date',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
        
    def validate(self, data):
        if data['from_base'] == data['to_base']:
            raise serializers.ValidationError("Cannot transfer to the same base")
        return data
        
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        transfer = super().create(validated_data)
        
        if transfer.status == 'completed':
            # Update inventory at both bases
            from_inventory, _ = Inventory.objects.get_or_create(
                base=transfer.from_base,
                equipment_type=transfer.equipment_type,
                defaults={'quantity': 0}
            )
            from_inventory.quantity -= transfer.quantity
            from_inventory.save()
            
            to_inventory, _ = Inventory.objects.get_or_create(
                base=transfer.to_base,
                equipment_type=transfer.equipment_type,
                defaults={'quantity': 0}
            )
            to_inventory.quantity += transfer.quantity
            to_inventory.save()
        
        return transfer
        
    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get('status', old_status)
        
        # If status changed to completed, update inventory
        if old_status != 'completed' and new_status == 'completed':
            from_inventory, _ = Inventory.objects.get_or_create(
                base=instance.from_base,
                equipment_type=instance.equipment_type,
                defaults={'quantity': 0}
            )
            from_inventory.quantity -= instance.quantity
            from_inventory.save()
            
            to_inventory, _ = Inventory.objects.get_or_create(
                base=instance.to_base,
                equipment_type=instance.equipment_type,
                defaults={'quantity': 0}
            )
            to_inventory.quantity += instance.quantity
            to_inventory.save()
        
        return super().update(instance, validated_data)


class AssignmentSerializer(serializers.ModelSerializer):
    base_name = serializers.CharField(source='base.name', read_only=True)
    equipment_name = serializers.CharField(source='equipment_type.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    outstanding_quantity = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'base', 'base_name', 'equipment_type', 'equipment_name',
            'personnel_name', 'personnel_id', 'assigned_quantity', 'returned_quantity',
            'outstanding_quantity', 'assignment_date', 'return_date',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'outstanding_quantity', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        assignment = super().create(validated_data)
        
        # Update inventory
        inventory, _ = Inventory.objects.get_or_create(
            base=assignment.base,
            equipment_type=assignment.equipment_type,
            defaults={'quantity': 0}
        )
        inventory.quantity -= assignment.assigned_quantity
        inventory.save()
        
        return assignment
        
    def update(self, instance, validated_data):
        old_returned = instance.returned_quantity
        new_returned = validated_data.get('returned_quantity', old_returned)
        
        # If returned quantity increased, add back to inventory
        if new_returned > old_returned:
            returned_diff = new_returned - old_returned
            inventory, _ = Inventory.objects.get_or_create(
                base=instance.base,
                equipment_type=instance.equipment_type,
                defaults={'quantity': 0}
            )
            inventory.quantity += returned_diff
            inventory.save()
        
        return super().update(instance, validated_data)


class ExpenditureSerializer(serializers.ModelSerializer):
    base_name = serializers.CharField(source='base.name', read_only=True)
    equipment_name = serializers.CharField(source='equipment_type.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Expenditure
        fields = [
            'id', 'base', 'base_name', 'equipment_type', 'equipment_name',
            'quantity', 'reason', 'expenditure_date',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        expenditure = super().create(validated_data)
        
        # Update inventory
        inventory, _ = Inventory.objects.get_or_create(
            base=expenditure.base,
            equipment_type=expenditure.equipment_type,
            defaults={'quantity': 0}
        )
        inventory.quantity -= expenditure.quantity
        inventory.save()
        
        return expenditure
