from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from matplotlib import widgets
from .models import Product,Comment

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('comment_body',)
        widgets = {
            'comment_body':forms.Textarea(attrs={'class':'form-control'}),
        }