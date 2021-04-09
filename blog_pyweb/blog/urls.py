from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    path('notes/', views.TablosView.as_view(), name='notes'),
    path('note/<int:note_id>/', views.TabloDetailView.as_view(), name='note'),
    path('note/add/', views.TabloEditorView.as_view(), name='add'),
    path('note/<int:note_id>/save/', views.TabloEditorView.as_view(), name='save'),
    path('comment/<int:note_id>/add/', views.CommentDetailView.as_view(), name='comment_add'),
    path('comment/<int:comment_id>/del/', views.CommentDetailView.as_view(), name='comment_del'),
]
