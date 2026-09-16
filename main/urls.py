from django.urls import path
from main.views import show_main, show_projects, create_project

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('projects/', show_projects, name="show_projects"),
    path('projects/add/', create_project, name="create_project"),
]
    