from unicodedata import name
from django.shortcuts import redirect, render, reverse
from django.http import JsonResponse
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .forms import * 
import datetime

@login_required(login_url='login')
def store(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)

@login_required(login_url='login')
def productDetail(request,pk):
	product = Product.objects.get(id=pk)
	num_comments = Comment.objects.filter(product=product).count()
	context = {'product':product, 'num_comments':num_comments}
	return render(request,'store/productDetail.html',context)

@login_required(login_url='login')
def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)


@login_required(login_url='login')
def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)


@login_required(login_url='login')
def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)

def registerPage(request):
	if request.user.is_authenticated:
		return redirect('store')
	else:
		form = CreateUserForm()

		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				form.save()
				user = form.cleaned_data.get('username')
				messages.success(request,'Account was created for '+user)
				return redirect('login')

		context ={'form':form}
		return render(request,'store/register.html',context)

def loginPage(request):
	if request.user.is_authenticated:
		return redirect('store')
	else:
		if request.method=='POST':
			username = request.POST.get('username')
			password = request.POST.get('password')

			user = authenticate(request,username=username,password=password)
			if user is not None:
				login(request,user)
				return redirect('store')
			else:
				messages.info(request,'Username OR Password is incorrect')
		context ={}
		return render(request,'store/login.html',context)


def logoutUser(request):
	logout(request)
	return redirect('login')

@login_required(login_url='login')
def add_comment(request,pk):
	product = Product.objects.get(id=pk)
	product_id = product.id
	form = CommentForm(instance=product)
	if request.method == 'POST':
		form = CommentForm(request.POST,instance=product)
		if form.is_valid():
			name = request.user.username
			body = form.cleaned_data['comment_body']
			c = Comment(product=product,commenter_name=name,comment_body=body,date_added=datetime.datetime.now())
			c.save()
			return redirect(reverse('productDetail',args=[product_id]))
		else:
			print('Form is invalid')
	else:
		form = CommentForm()
	

	context = {
		'form' :form
	}
	return render(request,'store/add_comment.html',context)

@login_required(login_url='login')
def delete_comment(request,pk):
	comment = Comment.objects.filter(product=pk).last()
	product_id = comment.product.id
	comment.delete()
	return redirect(reverse('productDetail',args=[product_id]))

@login_required(login_url='login')
def searchBar(request):
	if request.method=='GET':
		query = request.GET.get('query')
		if query:
			products = Product.objects.filter(name__icontains=query)
			context = {'products':products,}
			return render(request,'store/searchbar.html',context)
		else:
			print("No information to show")
			return render(request,'store/searchbar.html',{}) 
