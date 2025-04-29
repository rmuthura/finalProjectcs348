from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('album/', views.album_view, name='album_view'),
    path('update_song/<int:song_id>/', views.update_song, name='update_song'),
    path('short_songs_input/', views.filter_songs_by_duration, name='short_songs_input'),
    path('add_song/', views.add_song, name='add_song'),
    path('delete_song/<int:song_id>/', views.delete_song, name='delete_song'),
    path('create_playlist/', views.create_playlist, name='create_playlist'),
    path('playlist/<int:playlist_id>/', views.view_playlist, name='view_playlist'),
    path('add_album/', views.add_album, name='add_album'),
    path('delete_album/<int:album_id>/', views.delete_album, name='delete_album'),
    path('filter_by_genre/', views.filter_songs_by_genre, name='filter_by_genre'),
    path('filter_by_explicit/', views.filter_songs_by_explicit, name='filter_by_explicit'),
    path('add_artist/', views.add_artist, name='add_artist'),
    path('delete_artist/<int:artist_id>/', views.delete_artist, name='delete_artist'),
    path('delete_artist/', views.select_artist_to_delete, name='delete_artist_prompt'),
    path('delete_artist/<int:artist_id>/', views.delete_artist, name='delete_artist'),



]
