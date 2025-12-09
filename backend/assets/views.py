from rest_framework import viewsets, status, filters
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
    Assignment, Expenditure, UserRole
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer, BaseSerializer,
    EquipmentTypeSerializer, InventorySerializer, PurchaseSerializer,
    TransferSerializer, AssignmentSerializer, ExpenditureSerializer
)
from .permissions import IsAdmin, BaseAccessPermission, CanModifyAssignments


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
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'location']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
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
