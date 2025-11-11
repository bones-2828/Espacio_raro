from django.contrib import admin
from django.urls import path, include
from main import views
from rest_framework import routers
from main.api import ClientesViewSet

# --- API Router ---
router = routers.DefaultRouter()
router.register(r'clientes', ClientesViewSet, basename='clientes')

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),

    # Sitio general
    path('', views.homepage, name="homepage"),
    path('quickorder/', views.order, name="quickorder"),
    path('quickorder_success/', views.pedido_exitoso, name="pedido_exitoso"),

    # Autenticación
    path('login/', views.login_view, name="login_view"), 
    path('register/', views.register, name="register"), 
    path('logout/', views.logout_view, name='logout'),

    # Paneles
    path('dashboard/', views.dashboard, name="dashboard"),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/pedidos/', views.user_pedidos_list, name='user_pedidos_list'),
    path('user/pedidos/<int:pk>/', views.user_pedido_detail, name='user_pedido_detail'),

    # Perfil del usuario
    path('user/perfil/', views.user_perfil_edit, name='user_perfil_edit'),
    # Crear pedido desde cuenta de usuario
    path('user/quickorder/', views.user_quickorder, name='user_quickorder'),
    path('user/confirm/', views.user_confirm, name='user_confirm'),

    # CRUD Clientes
    path('clientes/', views.clientes_list, name='clientes_list'),
    path('clientes/nuevo/', views.clientes_create, name='clientes_create'),
    path('clientes/<int:pk>/', views.clientes_detail, name='clientes_detail'),
    path('clientes/<int:pk>/editar/', views.clientes_update, name='clientes_update'),
    path('clientes/<int:pk>/eliminar/', views.clientes_delete, name='clientes_delete'),
    
    # CRUD Productos
    path('productos/', views.productos_list, name='productos_list'),
    path('productos/nuevo/', views.productos_create, name='productos_create'),
    path('productos/editar/<int:id_producto>/', views.productos_update, name='productos_update'),
    path('productos/eliminar/<int:id_producto>/', views.productos_delete, name='productos_delete'),
    
    # CRUD Pedidos
    path('pedidos/', views.pedidos_list, name='pedidos_list'),
    path('pedidos/nuevo/', views.pedidos_create, name='pedidos_create'),
    path('pedidos/<int:pk>/', views.pedidos_detail, name='pedidos_detail'),
    path('pedidos/<int:pk>/editar/', views.pedidos_update, name='pedidos_update'),
    path('pedidos/<int:pk>/eliminar/', views.pedidos_delete, name='pedidos_delete'),

    # CRUD Detalles de Pedidos
    path('detalles_pedidos/', views.detalles_pedidos_list, name='detalles_pedidos_list'),
    path('detalles_pedidos/nuevo/', views.detalles_pedidos_create, name='detalles_pedidos_create'),
    path('detalles_pedidos/<int:pk>/editar/', views.detalles_pedidos_update, name='detalles_pedidos_update'),
    path('detalles_pedidos/<int:pk>/eliminar/', views.detalles_pedidos_delete, name='detalles_pedidos_delete'),

    # --- API REST ---
    path('api/', include(router.urls)),
]

