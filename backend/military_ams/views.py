from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def api_root(request):
    """
    Root endpoint that provides API information
    """
    return JsonResponse({
        'message': 'Military Asset Management System API',
        'version': '1.0',
        'status': 'active',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/v1/',
            'documentation': {
                'auth': '/api/v1/auth/',
                'setup': '/api/v1/setup/',
                'bases': '/api/v1/bases/',
                'equipment_types': '/api/v1/equipment-types/',
                'inventory': '/api/v1/inventory/',
                'purchases': '/api/v1/purchases/',
                'transfers': '/api/v1/transfers/',
                'assignments': '/api/v1/assignments/',
                'expenditures': '/api/v1/expenditures/',
                'dashboard': '/api/v1/dashboard/stats/',
            }
        }
    })
