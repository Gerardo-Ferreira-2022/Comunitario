from django.shortcuts import render, redirect
from folium.plugins import HeatMap
import random
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse
from .forms import TaskForm, FormModelForm
from .models import Task
import folium
from folium.plugins import FastMarkerCluster
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import FormModel
# Create your views here.

def generate_random_locations():
    # Coordenadas aproximadas de Santiago de Chile
    latitudes = [-33.5, -33.3]  # Rango de latitudes dentro de Santiago
    longitudes = [-70.75, -70.45]  # Rango de longitudes dentro de Santiago
    locations = []

    for _ in range(50):  # Crear 50 ubicaciones aleatorias
        lat = random.uniform(latitudes[0], latitudes[1])
        lon = random.uniform(longitudes[0], longitudes[1])
        locations.append((lat, lon))
    
    return locations

# Vista index
def index(request):
    # Definir el mapa centrado en Chile
    initialMap = folium.Map(location=[-33.45694, -70.64827], zoom_start=8)

    # Lista de coordenadas de los campus INACAP en Chile
    inacap_locations = [
        {"name": "INACAP Santiago Centro", "coords": [-33.4623, -70.6500]},
        {"name": "INACAP Maipú", "coords": [-33.4874, -70.8320]},
        {"name": "INACAP Puente Alto", "coords": [-33.6110, -70.5720]},
        {"name": "INACAP Vicuña Mackenna", "coords": [-33.4558, -70.6296]},
        {"name": "INACAP Ñuñoa", "coords": [-33.4644, -70.6155]},
        {"name": "INACAP San Bernardo", "coords": [-33.5991, -70.6095]},
        {"name": "INACAP Concepción", "coords": [-36.8272, -73.0477]},
        {"name": "INACAP Valparaíso", "coords": [-33.0361, -71.5510]},
        {"name": "INACAP Antofagasta", "coords": [-23.6557, -70.3959]},
        {"name": "INACAP La Serena", "coords": [-29.9045, -71.2507]},
        {"name": "INACAP Temuco", "coords": [-38.7389, -72.6007]},
        {"name": "INACAP Puerto Montt", "coords": [-41.4709, -72.9443]}
    ]

    # Agregar un marcador para cada campus de INACAP
    for location in inacap_locations:
        folium.Marker(
            location["coords"],
            popup=location["name"]
        ).add_to(initialMap)

    # Retornar el mapa como un objeto HTML
    context = {'map': initialMap._repr_html_()}
    return render(request, 'index.html', context)


# Vista menu.
@login_required
def menu(request):

    # Defino el mapa
    initialMap = folium.Map(location=[-33.45694, -70.64827], zoom_start=11)

    context = {'map':initialMap._repr_html_()}
    return render(request, 'menu.html', context)



def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                # Registro del usuario incluyendo el correo
                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1'],
                    email=request.POST['email']  # Guardar el email
                )
                user.save()
                login(request, user)
                return redirect('tasks')  # Cambiar por la vista o URL que desees redirigir
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    "error": 'El usuario ya existe'
                })
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'Las contraseñas no coinciden'
        })
    


def signout(request):
    logout(request)
    return redirect('signin')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user =authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Usuario o Contraceña incorrecta'
            })
        
        else:
            login(request, user)
            return redirect('menu')
        


@login_required
def tasks(request):
    # Obtener las tareas
    tasks = Task.objects.all()

    # Obtener el usuario actual
    user = request.user

    # Si el formulario se envía
    if request.method == 'POST':
        comment = request.POST.get('comment')  # Comentario
        lat = request.POST.get('lat')  # Latitud
        lon = request.POST.get('lon')  # Longitud

        # Verificar si el comentario está vacío
        if not comment:
            messages.error(request, "El comentario es obligatorio.")
        else:
            # Crear una nueva entrada en el modelo FormModel
            FormModel.objects.create(
                user=user,
                comment=comment,
                latitude=lat,
                longitude=lon
            )
            messages.success(request, "Comentario guardado correctamente.")

        # Redirigir después de guardar
        return redirect('tasks')  # Cambia 'tasks' por el nombre de la vista que desees

    # Contexto para la plantilla
    context = {
        'tasks': tasks,
        'user': user,
        'form_models': FormModel.objects.all()  # Asegúrate de pasar los objetos correctos
    }

    return render(request, 'tasks.html', context)



@login_required
def usuarios(request):
    # Si deseas obtener todos los usuarios:
    usuarios = User.objects.all()

    # Pasa los usuarios al contexto
    return render(request, 'usuarios.html', {'usuarios': usuarios})



# Vista para eliminar un usuario
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    usuario.delete()
    messages.success(request, 'Usuario eliminado exitosamente.')
    return redirect('usuarios')  # Redirige a la lista de usuarios



def actualizar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        nuevo_email = request.POST.get('email')
        is_superuser = request.POST.get('is_superuser') == 'on'
        is_active = request.POST.get('is_active') == 'on'

        # Actualizar los campos
        usuario.email = nuevo_email
        usuario.is_superuser = is_superuser
        usuario.is_active = is_active
        usuario.save()

        # Mensaje de éxito
        messages.success(request, f'Usuario {usuario.username} actualizado exitosamente.')
        return redirect('usuarios')  # Redirige a la lista de usuarios


# Vista para eliminar un comentario
@login_required
def eliminar_comentario(request, comentario_id):
    comentario = get_object_or_404(FormModel, id=comentario_id)
    comentario.delete()
    messages.success(request, 'Comentario eliminado exitosamente.')
    return redirect('tasks')  # Redirige a la lista de comentarios



# Vista para mostrar y actualizar un comentario
def actualizar_comentario(request, comentario_id):
    comentario = get_object_or_404(FormModel, id=comentario_id)

    if request.method == 'POST':
        # Si el formulario es enviado, actualizamos el comentario
        form = FormModelForm(request.POST, instance=comentario)
        if form.is_valid():
            form.save()  # Guarda el comentario actualizado
            messages.success(request, 'Comentario actualizado exitosamente.')
            return redirect('tasks')  # Redirige a la lista de tareas (o comentarios)
    else:
        # Si es GET, mostramos el formulario con los datos actuales
        form = FormModelForm(instance=comentario)

    return render(request, 'actualizar_comentario.html', {'form': form})



def editar_comentario(request, comentario_id):
    comentario = get_object_or_404(FormModel, id=comentario_id)

    if request.method == 'POST':
        comentario.comment = request.POST.get('comment')
        comentario.latitude = request.POST.get('latitude')
        comentario.longitude = request.POST.get('longitude')
        comentario.created_at = request.POST.get('created_at')
        comentario.save()

    # Asegúrate de pasar los datos del comentario al contexto
    context = {
        'comentario': comentario
    }
    
    return render(request, 'tasks.html', context)


def mapa_view(request):
    # Comprobar si la vista se llama
    print("Vista mapa_view llamada")

    form_models = FormModel.objects.all()
    print(form_models)  # Asegúrate de que esto se imprime en la consola
    return render(request, 'menu.html', {'form_models': form_models})


def obtener_ubicaciones(request):
    lugar = request.GET.get('lugar', '')
    ubicaciones = FormModel.objects.filter(address__icontains=lugar).values('latitude', 'longitude', 'comment')
    return JsonResponse(list(ubicaciones), safe=False)




def mapa_interactivo_view(request):
    # Definir el mapa centrado en Chile (por ejemplo, Santiago)
    initialMap = folium.Map(location=[-33.45694, -70.64827], zoom_start=8)

    # Retornar el mapa como un objeto HTML
    context = {'map': initialMap._repr_html_()}
    return render(request, 'menu.html', context)