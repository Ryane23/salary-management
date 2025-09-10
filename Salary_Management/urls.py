"""
URL configuration for Salary_Management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import FileResponse, HttpResponse
from django.views.decorators.cache import never_cache
import os

def serve_frontend_file(request, filename='index.html'):
    """Serve frontend HTML files"""
    file_path = os.path.join(settings.BASE_DIR, 'frontend', filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'))
    else:
        # If file doesn't exist, serve index.html (for SPA routing)
        index_path = os.path.join(settings.BASE_DIR, 'frontend', 'index.html')
        if os.path.exists(index_path):
            return FileResponse(open(index_path, 'rb'))
        else:
            return HttpResponse("Frontend not found. Please add HTML files to the frontend directory.", status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('payslip_reportcard.urls')),  # API endpoints (fixed path)
    
    # Frontend routes
    path('', never_cache(serve_frontend_file), {'filename': 'index.html'}, name='home'),
    path('<str:filename>', never_cache(serve_frontend_file), name='frontend_files'),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'frontend'))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
