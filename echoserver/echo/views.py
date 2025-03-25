from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Book, Cart, CartItem, Order, OrderItem
from .forms import BookForm, RegisterForm, LoginForm
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.contrib import messages
from django.core.exceptions import ValidationError
# Create your views here.
User = get_user_model()

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('book_list')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('book_list')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('book_list')

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

def book_list(request):
    books = Book.objects.all()
    paginator = Paginator(books, 5)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    return render(request, 'book_list.html', {'books': books})

@login_required
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'book_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'book_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')

@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')
        if username != user.username and User.objects.filter(username=username).exists():
            messages.error(request, 'Это имя пользователя уже занято')
            return redirect('profile')
        # Обновляем данные пользователя
        try:
            user.username = username
            user.email = email
            user.role = role
            user.full_clean()
            user.save()
            messages.success(request, 'Профиль успешно обновлен')
        except ValidationError as e:
            messages.error(request, f'Ошибка при обновлении профиля: {str(e)}')
        return redirect('profile')
    return render(request, 'profile.html')


@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('book_list')


# Просмотр корзины
@login_required
@login_required
def cart_view(request):
    # Получаем корзину пользователя или создаем новую, если она не существует
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    # Вычисляем общую стоимость с помощью F-выражений
    total = cart_items.aggregate(
        total=Sum(
            ExpressionWrapper(
                F('book__price') * F('quantity'),
                output_field=DecimalField()
            )
        )
    )['total'] or 0
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def remove_from_cart(request, item_id):
    # Получаем корзину пользователя
    cart = get_object_or_404(Cart, user=request.user)
    # Получаем элемент корзины
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    # Удаляем элемент
    cart_item.delete()
    messages.success(request, 'Книга удалена из корзины')
    return redirect('cart_view')

# Оформление заказа
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items:
        return redirect('cart_view')

    total = sum(item.book.price * item.quantity for item in cart_items)
    order = Order.objects.create(user=request.user, total_price=total)

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            book=item.book,
            quantity=item.quantity,
            price=item.book.price
        )

    cart_items.delete()
    return redirect('order_history')


# История заказов
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})