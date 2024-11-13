from django import forms
from django.core import validators
class Usuario(forms.Form):
    nombre=forms.CharField(
        validators=[
            validators.MinLengthValidator(5),
            validators.MaxLengthValidator(20)
        ]
    )
    telefono =forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number'}))
    nombre.widget.attrs['class']= 'form-control'
    email = forms.CharField()
    contraseña = forms.CharField()
    direccion =  forms.CharField()
