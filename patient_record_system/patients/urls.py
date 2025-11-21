from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('upload_choice/', views.upload_choice, name='upload_choice'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('upload/success/', views.upload_success, name='upload_success'),
    path('my-records/', views.my_records, name='my_records'),
    path('create-group/', views.create_group, name='create_group'),
    path('batch-upload/', views.batch_upload, name='batch_upload'),
    path('group/<int:group_id>/add/', views.add_to_group, name='add_to_group'),
    path('delete_group/<int:group_id>/', views.delete_group, name='delete_group'),
    path('group/<int:group_id>/download/', views.download_group, name='download_group'),
    path('batch-upload/', views.batch_upload, name='batch_upload'),
    path('ungrouped/', views.ungrouped_files, name='ungrouped_files'),
    path('delete/<int:file_id>/', views.delete_file, name='delete_file'),
    path('remove/<int:file_id>/', views.remove_from_group, name='remove_from_group'),
    path('group/<int:group_id>/delete_all/', views.delete_all_files_in_group, name='delete_all_files_in_group'),
    path("ungrouped/download/", views.download_ungrouped_zip, name="download_ungrouped_zip"),
    path("ungrouped/delete-all/", views.delete_all_ungrouped, name="delete_all_ungrouped"),

]
