from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    register, login, current_user, dashboard_stats, role_choices,
    initialize_role_codes, get_role_codes, populate_demo_bases,
    BaseViewSet, EquipmentTypeViewSet, InventoryViewSet,
    PurchaseViewSet, TransferViewSet, AssignmentViewSet, ExpenditureViewSet
)

router = DefaultRouter()
router.register(r'bases', BaseViewSet, basename='base')
router.register(r'equipment-types', EquipmentTypeViewSet, basename='equipmenttype')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'purchases', PurchaseViewSet, basename='purchase')
router.register(r'transfers', TransferViewSet, basename='transfer')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'expenditures', ExpenditureViewSet, basename='expenditure')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/user/', current_user, name='current_user'),
    path('auth/roles/', role_choices, name='role_choices'),
    
    # Role code endpoints (public for initialization)
    path('auth/init-role-codes/', initialize_role_codes, name='initialize_role_codes'),
    path('auth/role-codes/', get_role_codes, name='get_role_codes'),
    
    # Setup endpoints (public for initial setup)
    path('setup/populate-bases/', populate_demo_bases, name='populate_demo_bases'),
    
    # Dashboard
    path('dashboard/stats/', dashboard_stats, name='dashboard_stats'),
    
    # Router URLs
    path('', include(router.urls)),
]
