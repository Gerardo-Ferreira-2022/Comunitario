from django.forms import ModelForm
from .models import Task, FormModel
from django import forms


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['rut', 'email', 'descripcion', 'latitud', 'longitud', ]



class FormModelForm(forms.ModelForm):
    class Meta:
        model = FormModel
        fields = ['comment', 'latitude', 'longitude']
    
    # Validación personalizada para el campo 'comment'
    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if not comment:
            raise forms.ValidationError('El comentario es obligatorio.')
        return comment