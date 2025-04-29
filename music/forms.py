
from django import forms
from .models import Song, Album


#Form for updating songs
class SongUpdateForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'album', 'artist', 'duration', 'genre', 'explicit']



#User input for adding songs
class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'album', 'artist', 'duration', 'genre', 'explicit']


#User input for playlist
class AddToPlaylistForm(forms.Form):
    playlist_name = forms.CharField(max_length=100)
    song_title = forms.CharField(max_length=100)


#User input for album
class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['name', 'artist', 'release_year']