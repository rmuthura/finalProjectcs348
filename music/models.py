from django.db import models

#Artist Object
class Artist(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

#Album object
class Album(models.Model):
    name = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    release_year = models.IntegerField()

    def __str__(self):
        return f"{self.name} by {self.artist.name}"

#Song object
class Song(models.Model):
    title = models.CharField(max_length=100)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    duration = models.DurationField()
    genre = models.CharField(max_length=50, default="Hip-Hop")
    explicit = models.BooleanField(default=True)

    def __str__(self):
        return self.title

#Playlist object, name of playlist
class Playlist(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

#Playlist object when songs are entered, linking both playlist and song objects M:M
class PlaylistEntry(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='entries')
    song = models.ForeignKey('Song', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.song.title} in {self.playlist.name}"

