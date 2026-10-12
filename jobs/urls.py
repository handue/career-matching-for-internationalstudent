from django.urls import path
from . import views

app_name = "jobs"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("api/collection-jobs/", views.create_collection, name="create_collection"),
    path("api/collection-jobs/<uuid:job_id>/", views.collection_status, name="collection_status"),
]
