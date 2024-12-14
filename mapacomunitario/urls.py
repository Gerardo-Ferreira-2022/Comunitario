from django.urls import path
from .views import index, menu, signin, signup, signout, tasks, usuarios
from . import views


urlpatterns = [
    path('', index, name='home'),
    path('menu/', menu, name='menu'),
    path('signin/', signin, name='signin'),
    path('signup/', signup, name='signup'),
    path('logout/', signout, name='logout'),
    path('tasks/', tasks, name='tasks'),
    path('usuarios/', usuarios, name='usuarios'),
    path('eliminar_usuario/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('actualizar_usuario/<int:user_id>/', views.actualizar_usuario, name='actualizar_usuario'),
    path('eliminar_comentario/<int:comentario_id>/', views.eliminar_comentario, name='eliminar_comentario'),
    path('actualizar_comentario/<int:comentario_id>/', views.actualizar_comentario, name='actualizar_comentario'),
    path('obtener_ubicaciones/', views.obtener_ubicaciones, name='obtener_ubicaciones'),
    path('mapa/', views.mapa_interactivo_view, name='mapa_interactivo_view'),
]