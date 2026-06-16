from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    is_journalist = forms.BooleanField(required=False, label="Je suis journaliste")
    is_media_organization = forms.BooleanField(required=False, label="مؤسسة إعلامية / صحيفة")
    organization = forms.CharField(max_length=200, required=False, label="Organisation / Media")

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'is_journalist', 'is_media_organization', 'organization')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'bio', 'organization', 'avatar')