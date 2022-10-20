from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def spotify(request):
    return render(request, 'spotify.html')


def tutorial(request):
    return render(request, 'tutorial.html')


def judge(request):
    return render(request, 'judge.html')


def profile(request):
    return render(request, 'profile.html')


def playlist(request):
    return render(request, 'playlist.html')

def bar(request):
    return render(request, 'bar.html')

def graph(request):
    return render(request, 'graph.html')
    
def artist(request):
    return render(request, 'artist.html')
