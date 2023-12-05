from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    #departement = forms.CharField(max_length=50, help_text='Required')

    class Meta:
        model = User
        fields = ('first_name', 'username', 'password1', 'password2', 'is_superuser', 'is_staff')

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        # user.departement = self.cleaned_data['departement']
        user.first_name = self.cleaned_data['first_name'].upper()
        user.username = self.cleaned_data['username'].lower()
        if commit:
            user.save()
        return user

    '''def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})'''


class UpdatePasswordForm(PasswordChangeForm):
    pass
