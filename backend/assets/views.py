from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q, Sum, F
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime

from .models import (
    Base, EquipmentType, Inventory, Purchase, Transfer,
    Assignment, Expenditure, UserRole, RoleCode
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer, BaseSerializer,
    EquipmentTypeSerializer, InventorySerializer, PurchaseSerializer,
    TransferSerializer, AssignmentSerializer, ExpenditureSerializer
)
from .permissions import IsAdmin, BaseAccessPermission, CanModifyAssignments


class BaseListPermission(permissions.BasePermission):
    """
    Allow unauthenticated users to list bases (for signup).
    Require authentication for all other operations.
    """
    def has_permission(self, request, view):
        # Allow anyone to list bases (needed for signup page)
        if view.action == 'list':
            return True
        # Require authentication for all other operations
        return request.user and request.user.is_authenticated


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login user and return JWT tokens"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    
    return Response(
        {'error': 'Invalid credentials'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current user details"""
    return Response(UserSerializer(request.user).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def role_choices(request):
    """Get available role choices for signup"""
    return Response({
        'roles': [
            {'value': role[0], 'label': role[1]}
            for role in UserRole.ROLE_CHOICES
        ]
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def initialize_role_codes(request):
    """Initialize default role codes (public endpoint for first-time setup)"""
    # Check if role codes already exist
    if RoleCode.objects.exists():
        return Response({
            'message': 'Role codes already initialized',
            'role_codes': list(RoleCode.objects.values('role', 'code', 'is_active'))
        })
    
    # Create default role codes
    role_codes_data = [
        {
            'role': 'admin',
            'code': 'ADMIN2024',
            'description': 'Administrator access code',
            'is_active': True
        },
        {
            'role': 'base_commander',
            'code': 'BASECMD2024',
            'description': 'Base Commander access code',
            'is_active': True
        },
        {
            'role': 'logistics_officer',
            'code': 'LOGISTICS2024',
            'description': 'Logistics Officer access code',
            'is_active': True
        },
    ]
    
    created_codes = []
    for role_data in role_codes_data:
        role_code, created = RoleCode.objects.get_or_create(
            role=role_data['role'],
            defaults={
                'code': role_data['code'],
                'description': role_data['description'],
                'is_active': role_data['is_active']
            }
        )
        created_codes.append({
            'role': role_code.role,
            'code': role_code.code,
            'is_active': role_code.is_active
        })
    
    return Response({
        'message': 'Role codes initialized successfully',
        'role_codes': created_codes
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_role_codes(request):
    """Get all active role codes (for signup page)"""
    role_codes = RoleCode.objects.filter(is_active=True).values('role', 'code')
    return Response({
        'role_codes': list(role_codes)
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def populate_demo_bases(request):
    """Populate demo bases (public endpoint for initial setup)"""
    # Check if bases already exist
    existing_count = Base.objects.filter(is_deleted=False).count()
    if existing_count > 0:
        return Response({
            'message': f'Bases already exist ({existing_count} bases found)',
            'bases_count': existing_count,
            'bases': list(Base.objects.filter(is_deleted=False).values('id', 'name', 'code', 'location'))
        })
    
    # Demo bases data
    bases_data = [
        {'name': 'Alpha Base', 'location': 'North Region', 'code': 'ALPHA-01'},
        {'name': 'Bravo Base', 'location': 'South Region', 'code': 'BRAVO-02'},
        {'name': 'Charlie Base', 'location': 'East Region', 'code': 'CHARLIE-03'},
        {'name': 'Fort Alpha', 'location': 'Northern Region', 'code': 'FA-001'},
        {'name': 'Fort Bravo', 'location': 'Southern Region', 'code': 'FB-002'},
        {'name': 'Fort Charlie', 'location': 'Eastern Region', 'code': 'FC-003'},
        {'name': 'Fort Delta', 'location': 'Western Region', 'code': 'FD-004'},
        {'name': 'Fort Echo', 'location': 'Central Region', 'code': 'FE-005'},
        {'name': 'Naval Base Omega', 'location': 'Coastal Region', 'code': 'NBO-006'},
        {'name': 'Air Force Base Zulu', 'location': 'Highland Region', 'code': 'AFB-007'},
    ]
    
    created_bases = []
    for base_data in bases_data:
        # Check if base already exists by code
        if not Base.objects.filter(code=base_data['code']).exists():
            base = Base.objects.create(**base_data)
            created_bases.append({
                'id': base.id,
                'name': base.name,
                'code': base.code,
                'location': base.location
            })
    
    total_count = Base.objects.filter(is_deleted=False).count()
    
    return Response({
        'message': f'Successfully created {len(created_bases)} demo bases',
        'created_count': len(created_bases),
        'total_count': total_count,
        'bases': created_bases
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def populate_equipment_types(request):
    """Populate demo equipment types (public endpoint for initial setup)"""
    from .models import EquipmentType
    
    # Check if equipment types already exist
    existing_count = EquipmentType.objects.filter(is_deleted=False).count()
    if existing_count > 0:
        return Response({
            'message': f'Equipment types already exist ({existing_count} types found)',
            'equipment_count': existing_count,
            'equipment_types': list(EquipmentType.objects.filter(is_deleted=False).values('id', 'name', 'description', 'unit'))
        })
    
    # Demo equipment types data
    equipment_types_data = [
        {'name': 'M4 Carbine', 'description': 'Standard issue rifle', 'unit': 'units'},
        {'name': 'M9 Pistol', 'description': 'Standard issue sidearm', 'unit': 'units'},
        {'name': 'Body Armor', 'description': 'Protective vest', 'unit': 'units'},
        {'name': 'Helmet', 'description': 'Combat helmet', 'unit': 'units'},
        {'name': 'Night Vision Goggles', 'description': 'NVG equipment', 'unit': 'units'},
        {'name': 'Radio Equipment', 'description': 'Communication device', 'unit': 'units'},
        {'name': 'First Aid Kit', 'description': 'Medical supplies', 'unit': 'kits'},
        {'name': 'Ammunition (5.56mm)', 'description': 'Rifle ammunition', 'unit': 'rounds'},
        {'name': 'Ammunition (9mm)', 'description': 'Pistol ammunition', 'unit': 'rounds'},
        {'name': 'MRE (Meals Ready to Eat)', 'description': 'Field rations', 'unit': 'meals'},
    ]
    
    created_equipment = []
    for eq_data in equipment_types_data:
        if not EquipmentType.objects.filter(name=eq_data['name']).exists():
            equipment = EquipmentType.objects.create(**eq_data)
            created_equipment.append({
                'id': equipment.id,
                'name': equipment.name,
                'description': equipment.description,
                'unit': equipment.unit
            })
    
    total_count = EquipmentType.objects.filter(is_deleted=False).count()
    
    return Response({
        'message': f'Successfully created {len(created_equipment)} equipment types',
        'created_count': len(created_equipment),
        'total_count': total_count,
        'equipment_types': created_equipment
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def seed_transaction_data(request):
    """Seed demo transaction data (purchases, transfers, assignments, expenditures)"""
    from datetime import timedelta
    import random
    
    user = request.user
    
    # Get existing data
    bases = list(Base.objects.filter(is_deleted=False))
    equipment_types = list(EquipmentType.objects.filter(is_deleted=False))
    
    if not bases or not equipment_types:
        return Response({
            'error': 'Please ensure bases and equipment types exist first!',
            'bases_count': len(bases),
            'equipment_types_count': len(equipment_types)
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if data already exists
    existing_purchases = Purchase.objects.filter(is_deleted=False).count()
    existing_transfers = Transfer.objects.filter(is_deleted=False).count()
    
    if existing_purchases > 20 or existing_transfers > 10:
        return Response({
            'message': 'Transaction data already exists',
            'purchases': existing_purchases,
            'transfers': existing_transfers,
            'assignments': Assignment.objects.filter(is_deleted=False).count(),
            'expenditures': Expenditure.objects.filter(is_deleted=False).count()
        })
    
    created_data = {
        'purchases': 0,
        'transfers': 0,
        'assignments': 0,
        'expenditures': 0
    }
    
    # Create Purchases (30 records over the last 90 days)
    for i in range(30):
        days_ago = random.randint(1, 90)
        purchase_date = datetime.now().date() - timedelta(days=days_ago)
        
        base = random.choice(bases)
        equipment_type = random.choice(equipment_types)
        quantity = random.randint(10, 500)
        
        purchase = Purchase.objects.create(
            base=base,
            equipment_type=equipment_type,
            quantity=quantity,
            supplier=random.choice([
                'Defense Supplies Inc.',
                'Military Equipment Corp.',
                'Global Arms Ltd.',
                'Strategic Resources Co.',
                'National Defense Suppliers',
                'Allied Equipment Group'
            ]),
            purchase_date=purchase_date,
            created_by=user
        )
        
        # Update inventory
        inventory, created = Inventory.objects.get_or_create(
            base=base,
            equipment_type=equipment_type,
            defaults={'quantity': 0}
        )
        inventory.quantity += quantity
        inventory.save()
        created_data['purchases'] += 1
    
    # Create Transfers (20 records)
    for i in range(20):
        days_ago = random.randint(1, 60)
        transfer_date = datetime.now().date() - timedelta(days=days_ago)
        
        from_base = random.choice(bases)
        to_base = random.choice([b for b in bases if b != from_base])
        
        Transfer.objects.create(
            from_base=from_base,
            to_base=to_base,
            equipment_type=random.choice(equipment_types),
            quantity=random.randint(5, 100),
            status=random.choice(['pending', 'in_transit', 'completed']),
            transfer_date=transfer_date,
            created_by=user
        )
        created_data['transfers'] += 1
    
    # Create Assignments (25 records)
    personnel_names = [
        'Sgt. John Smith', 'Cpl. Sarah Johnson', 'Lt. Michael Brown',
        'Pvt. Emily Davis', 'Sgt. David Wilson', 'Cpl. Jessica Martinez',
        'Lt. Robert Anderson', 'Pvt. Amanda Taylor', 'Sgt. Christopher Lee',
        'Cpl. Jennifer White', 'Lt. Matthew Harris', 'Pvt. Ashley Clark',
        'Sgt. Daniel Lewis', 'Cpl. Melissa Walker', 'Lt. James Hall'
    ]
    
    for i in range(25):
        days_ago = random.randint(1, 120)
        assignment_date = datetime.now().date() - timedelta(days=days_ago)
        
        assigned_qty = random.randint(1, 20)
        returned_qty = random.randint(0, assigned_qty) if random.random() > 0.3 else 0
        
        return_date = None
        if returned_qty > 0:
            return_date = assignment_date + timedelta(days=random.randint(7, 60))
        
        Assignment.objects.create(
            base=random.choice(bases),
            equipment_type=random.choice(equipment_types),
            personnel_name=random.choice(personnel_names),
            personnel_id=f'MIL-{random.randint(10000, 99999)}',
            assigned_quantity=assigned_qty,
            returned_quantity=returned_qty,
            assignment_date=assignment_date,
            return_date=return_date,
            created_by=user
        )
        created_data['assignments'] += 1
    
    # Create Expenditures (15 records)
    expenditure_reasons = [
        'Training Exercise',
        'Combat Operations',
        'Equipment Testing',
        'Maintenance and Repair',
        'Emergency Response',
        'Field Operations',
        'Tactical Drills',
        'Equipment Damage',
        'Lost in Field',
        'Routine Consumption'
    ]
    
    for i in range(15):
        days_ago = random.randint(1, 90)
        expenditure_date = datetime.now().date() - timedelta(days=days_ago)
        
        Expenditure.objects.create(
            base=random.choice(bases),
            equipment_type=random.choice(equipment_types),
            quantity=random.randint(1, 50),
            reason=random.choice(expenditure_reasons),
            expenditure_date=expenditure_date,
            created_by=user
        )
        created_data['expenditures'] += 1
    
    return Response({
        'message': 'Successfully created transaction data',
        'created': created_data,
        'totals': {
            'purchases': Purchase.objects.filter(is_deleted=False).count(),
            'transfers': Transfer.objects.filter(is_deleted=False).count(),
            'assignments': Assignment.objects.filter(is_deleted=False).count(),
            'expenditures': Expenditure.objects.filter(is_deleted=False).count(),
            'inventory_items': Inventory.objects.count()
        }
    }, status=status.HTTP_201_CREATED)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics"""
    user = request.user
    
    # Get filters from query params
    base_id = request.query_params.get('base_id')
    equipment_type_id = request.query_params.get('equipment_type_id')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    # Filter bases based on user role
    try:
        user_role = user.role
        if user_role.role == 'admin':
            bases = Base.objects.filter(is_deleted=False)
        elif user_role.role == 'base_commander':
            bases = Base.objects.filter(id=user_role.assigned_base.id, is_deleted=False)
        else:
            bases = Base.objects.filter(is_deleted=False)
    except UserRole.DoesNotExist:
        return Response({'error': 'User role not found'}, status=status.HTTP_403_FORBIDDEN)
    
    # Apply base filter
    if base_id:
        bases = bases.filter(id=base_id)
    
    # Build query filters
    filters = Q(base__in=bases)
    if equipment_type_id:
        filters &= Q(equipment_type_id=equipment_type_id)
    
    date_filters = Q()
    if start_date:
        date_filters &= Q(created_at__gte=start_date)
    if end_date:
        date_filters &= Q(created_at__lte=end_date)
    
    # Calculate statistics
    inventory_total = Inventory.objects.filter(
        base__in=bases
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    purchases_total = Purchase.objects.filter(
        filters & date_filters, is_deleted=False
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    transfers_in = Transfer.objects.filter(
        Q(to_base__in=bases) & date_filters,
        status='completed',
        is_deleted=False
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    transfers_out = Transfer.objects.filter(
        Q(from_base__in=bases) & date_filters,
        status='completed',
        is_deleted=False
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    assigned_total = Assignment.objects.filter(
        filters & date_filters, is_deleted=False
    ).aggregate(total=Sum(F('assigned_quantity') - F('returned_quantity')))['total'] or 0
    
    expended_total = Expenditure.objects.filter(
        filters & date_filters, is_deleted=False
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    # Calculate opening and closing balance
    # For simplicity, opening balance = current inventory - net movement
    net_movement = purchases_total + transfers_in - transfers_out
    opening_balance = inventory_total - net_movement
    closing_balance = inventory_total
    
    # Get breakdown data
    purchases_list = Purchase.objects.filter(
        filters & date_filters, is_deleted=False
    ).values('equipment_type__name').annotate(total=Sum('quantity'))
    
    transfers_in_list = Transfer.objects.filter(
        Q(to_base__in=bases) & date_filters,
        status='completed',
        is_deleted=False
    ).values('equipment_type__name').annotate(total=Sum('quantity'))
    
    transfers_out_list = Transfer.objects.filter(
        Q(from_base__in=bases) & date_filters,
        status='completed',
        is_deleted=False
    ).values('equipment_type__name').annotate(total=Sum('quantity'))
    
    return Response({
        'opening_balance': float(opening_balance),
        'closing_balance': float(closing_balance),
        'net_movement': float(net_movement),
        'assigned_total': float(assigned_total),
        'expended_total': float(expended_total),
        'breakdown': {
            'purchases': list(purchases_list),
            'transfers_in': list(transfers_in_list),
            'transfers_out': list(transfers_out_list),
        }
    })


class BaseViewSet(viewsets.ModelViewSet):
    """ViewSet for Base model"""
    queryset = Base.objects.filter(is_deleted=False)
    serializer_class = BaseSerializer
    permission_classes = [BaseListPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'location']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Only filter by user role if user is authenticated
        if user.is_authenticated:
            try:
                user_role = user.role
                if user_role.role == 'base_commander':
                    # Base commanders only see their assigned base
                    queryset = queryset.filter(id=user_role.assigned_base.id)
            except UserRole.DoesNotExist:
                pass
        
        return queryset
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_deleted = True
        instance.save()


class EquipmentTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for EquipmentType model"""
    queryset = EquipmentType.objects.filter(is_deleted=False)
    serializer_class = EquipmentTypeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_deleted = True
        instance.save()


class InventoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Inventory model (read-only)"""
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['base', 'equipment_type']
    ordering_fields = ['base__name', 'equipment_type__name', 'quantity']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        try:
            user_role = user.role
            if user_role.role == 'base_commander':
                # Base commanders only see their assigned base
                queryset = queryset.filter(base=user_role.assigned_base)
        except UserRole.DoesNotExist:
            pass
        
        return queryset


class PurchaseViewSet(viewsets.ModelViewSet):
    """ViewSet for Purchase model"""
    queryset = Purchase.objects.filter(is_deleted=False)
    serializer_class = PurchaseSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['base', 'equipment_type']
    ordering_fields = ['purchase_date', 'created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Apply date filters
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(purchase_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(purchase_date__lte=end_date)
        
        try:
            user_role = user.role
            if user_role.role == 'base_commander':
                queryset = queryset.filter(base=user_role.assigned_base)
        except UserRole.DoesNotExist:
            pass
        
        return queryset
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_deleted = True
        instance.save()


class TransferViewSet(viewsets.ModelViewSet):
    """ViewSet for Transfer model"""
    queryset = Transfer.objects.filter(is_deleted=False)
    serializer_class = TransferSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['from_base', 'to_base', 'equipment_type', 'status']
    ordering_fields = ['transfer_date', 'created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Apply date filters
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(transfer_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(transfer_date__lte=end_date)
        
        try:
            user_role = user.role
            if user_role.role == 'base_commander':
                # Show transfers involving their base
                queryset = queryset.filter(
                    Q(from_base=user_role.assigned_base) | Q(to_base=user_role.assigned_base)
                )
        except UserRole.DoesNotExist:
            pass
        
        return queryset
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_deleted = True
        instance.save()


class AssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Assignment model"""
    queryset = Assignment.objects.filter(is_deleted=False)
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated, CanModifyAssignments]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['base', 'equipment_type']
    ordering_fields = ['assignment_date', 'created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Apply date filters
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(assignment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(assignment_date__lte=end_date)
        
        try:
            user_role = user.role
            if user_role.role == 'base_commander':
                queryset = queryset.filter(base=user_role.assigned_base)
        except UserRole.DoesNotExist:
            pass
        
        return queryset
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_deleted = True
        instance.save()


class ExpenditureViewSet(viewsets.ModelViewSet):
    """ViewSet for Expenditure model"""
    queryset = Expenditure.objects.filter(is_deleted=False)
    serializer_class = ExpenditureSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['base', 'equipment_type']
    ordering_fields = ['expenditure_date', 'created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Apply date filters
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(expenditure_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(expenditure_date__lte=end_date)
        
        try:
            user_role = user.role
            if user_role.role == 'base_commander':
                queryset = queryset.filter(base=user_role.assigned_base)
        except UserRole.DoesNotExist:
            pass
        
        return queryset
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_deleted = True
        instance.save()
