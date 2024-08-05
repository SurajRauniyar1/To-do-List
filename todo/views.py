from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .models import todo
import datetime
from django.utils.datastructures import MultiValueDictKeyError


def home(request):
    if request.user.is_authenticated:
        return redirect('current_todos')
    else:
        return render(request, 'todo/index.html')

# Auth

def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html',)
    else:
        # Create a new user
        if request.POST['password1']==request.POST['password2']:
            try:
                new_user = User.objects.create_user(request.POST['username'], password = request.POST['password1'])
                new_user.save()
                login(request, new_user)
                return redirect(current_todos)
                
            except IntegrityError:
                return render(request, 'todo/signupuser.html', {'error': 'Username already taken'})
        else:
            return render(request, 'todo/signupuser.html', {'error': 'Passwords did not match'})

def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html')
    elif request.method == 'POST':
        user = authenticate(request, username=request.POST['username'] , password=request.POST['password'])
        if not user:
            return render(request, 'todo/loginuser.html', {'error' : 'Invalid username/password'})
        else:
            login(request, user)
            return redirect('current_todos')

def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

# Listing stuff

def current_todos(request):
    if request.user.is_authenticated:
        todo_objects = todo.objects.filter(author = request.user)
        todo_objects_to_send = []
        for todo_obj in todo_objects:
            if not todo_obj.datecompleted:
                todo_objects_to_send.append(todo_obj)
        context = {
            'todos' : todo_objects_to_send
        }
        return render(request, 'todo/current_todos.html', context)
    else: 
        return redirect('loginuser')

def detail(request, todo_id : int):
    if request.method == 'GET':
        if request.user.is_authenticated:
            target_todo_object = get_object_or_404(todo, pk=todo_id)
            return render(request, 'todo/detail.html', {'todo' : target_todo_object})
    else:
        if request.user.is_authenticated:
            print(request.POST)

def completed(request):
    if request.user.is_authenticated:
        todo_objects = todo.objects.filter(author = request.user)
        todos = []
        for todo_entry in todo_objects:
            if todo_entry.datecompleted:
                todos.append(todo_entry)
        return render(request, 'todo/completed_todos.html', {'todos' : todos})

def create_todo(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return render(request, 'todo/create_todo.html')
        else:
            return redirect('loginuser')
    elif request.method == 'POST':
        new_todo = todo()
        new_todo.title = request.POST['titles']
        new_todo.memo = request.POST['memo']
        try:
            if request.POST['Important']:
                new_todo.important = True
        except MultiValueDictKeyError:
            new_todo.important = False
        new_todo.author = request.user
        new_todo.save()
        return redirect('current_todos')
        

# Actions

def complete_todo(request, todo_id : int):
    if request.method == 'POST':
        todo_obj = get_object_or_404(todo, pk=todo_id)
        if todo_obj.author == request.user:
            todo_obj.datecompleted = datetime.datetime.now()
            todo_obj.save()
            return redirect('current_todos')

def delete_todo(request, todo_id: int):
    if request.method == 'POST':
        todo_obj = get_object_or_404(todo, pk=todo_id)
        if todo_obj.author == request.user:
            todo_obj.delete()
            return redirect('current_todos')

def edit_todo(request, todo_id : int):
    if request.method == 'GET' and request.user.is_authenticated:
        todo_obj = get_object_or_404(todo, pk = todo_id)
        if todo_obj.author == request.user:
            return render(request, 'todo/edit_todo.html', {'todo' : todo_obj})
    if request.method == 'POST' and request.user.is_authenticated:
        todo_obj = get_object_or_404(todo, pk=todo_id)
        if todo_obj.author == request.user:
            todo_obj.title = request.POST['titles']
            todo_obj.memo = request.POST['memo']
            todo_obj.save()
            return redirect('current_todos')
