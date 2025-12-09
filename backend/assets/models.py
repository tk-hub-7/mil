from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class BaseModel(models.Model):
    """Abstract base model with common fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        abstract = True


class Base(BaseModel):
    """Military base information"""
    name = models.CharField(max_length=200, unique=True)
    location = models.CharField(max_length=300)
    code = models.CharField(max_length=50, unique=True)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.code})"


class EquipmentType(BaseModel):
    """Equipment type/category"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=50, default='units')  # e.g., units, kg, liters
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name


class Inventory(models.Model):
    """Current inventory levels at each base"""
    base = models.ForeignKey(Base, on_delete=models.CASCADE, related_name='inventory')
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['base', 'equipment_type']
        ordering = ['base', 'equipment_type']
        verbose_name_plural = 'Inventories'
        
    def __str__(self):
        return f"{self.base.name} - {self.equipment_type.name}: {self.quantity}"


class Purchase(BaseModel):
    """Asset purchase records"""
    base = models.ForeignKey(Base, on_delete=models.CASCADE, related_name='purchases')
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.CASCADE, related_name='purchases')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    supplier = models.CharField(max_length=300)
    purchase_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='purchases_created')
    
    class Meta:
        ordering = ['-purchase_date']
        
    def __str__(self):
        return f"Purchase: {self.equipment_type.name} - {self.quantity} @ {self.base.name}"


class Transfer(BaseModel):
    """Asset transfers between bases"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    from_base = models.ForeignKey(Base, on_delete=models.CASCADE, related_name='transfers_out')
    to_base = models.ForeignKey(Base, on_delete=models.CASCADE, related_name='transfers_in')
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.CASCADE, related_name='transfers')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transfer_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transfers_created')
    
    class Meta:
        ordering = ['-transfer_date']
        
    def __str__(self):
        return f"Transfer: {self.equipment_type.name} from {self.from_base.name} to {self.to_base.name}"


class Assignment(BaseModel):
    """Asset assignments to personnel"""
    base = models.ForeignKey(Base, on_delete=models.CASCADE, related_name='assignments')
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.CASCADE, related_name='assignments')
    personnel_name = models.CharField(max_length=200)
    personnel_id = models.CharField(max_length=100, blank=True)
    assigned_quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    returned_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    assignment_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assignments_created')
    
    class Meta:
        ordering = ['-assignment_date']
        
    def __str__(self):
        return f"Assignment: {self.equipment_type.name} to {self.personnel_name}"
    
    @property
    def outstanding_quantity(self):
        return self.assigned_quantity - self.returned_quantity


class Expenditure(BaseModel):
    """Expended/consumed assets"""
    base = models.ForeignKey(Base, on_delete=models.CASCADE, related_name='expenditures')
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.CASCADE, related_name='expenditures')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    reason = models.TextField()
    expenditure_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='expenditures_created')
    
    class Meta:
        ordering = ['-expenditure_date']
        
    def __str__(self):
        return f"Expenditure: {self.equipment_type.name} - {self.quantity} @ {self.base.name}"


class UserRole(models.Model):
    """User role assignments with base restrictions"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('base_commander', 'Base Commander'),
        ('logistics_officer', 'Logistics Officer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    assigned_base = models.ForeignKey(Base, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__username']
        
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class RoleCode(models.Model):
    """Role codes for signup verification"""
    role = models.CharField(max_length=20, choices=UserRole.ROLE_CHOICES, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['role']
        
    def __str__(self):
        return f"{self.get_role_display()} - {self.code}"


class APILog(models.Model):
    """API request/response logging for audit trail"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    endpoint = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    request_body = models.TextField(blank=True)
    response_body = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"
