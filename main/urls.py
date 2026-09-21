from django.urls import path
from main.views import (
    show_main, 
    show_projects, 
    create_project, 
    create_peer, 
    update_project, 
    delete_project, 
    get_projects_json, 
    get_projects_xml
)
app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('projects/', show_projects, name="show_projects"),
    path('projects/add/', create_project, name="create_project"),
    path('projects/<uuid:project_id>/edit/', update_project, name="update_project"),
    path('projects/<uuid:project_id>/delete/', delete_project, name="delete_project"),
    path('api/projects/', get_projects_json, name="get_projects_json"),
    path('api/projects/xml/', get_projects_xml, name="get_projects_xml"),
    path('peers/add/', create_peer, name="create_peer"),
]
