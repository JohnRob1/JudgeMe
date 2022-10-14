from django.shortcuts import render, redirect, HttpResponseRedirect


def index(request):
    return render(request, 'base.html')
