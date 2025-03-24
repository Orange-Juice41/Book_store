from django import forms
from .models import Book, User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class BookForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Название книги'
        self.fields['author'].label = 'Автор книги'
        self.fields['price'].label = 'Цена'
    class Meta:
        model = Book
        fields = ['title', 'author', 'price']

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    role = forms.ChoiceField(
        label="Роль",
        choices=[
            ('user', 'Обычный пользователь'),
            ('admin', 'Админ'),
        ],
        widget=forms.RadioSelect,  # Используем radio buttons
        initial='user',  # Значение по умолчанию
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'
        self.fields['role'].label = 'Роль'
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'
        self.fields['password'].label = 'Пароль'
    class Meta:
        model = User
        fields = ['username', 'password']