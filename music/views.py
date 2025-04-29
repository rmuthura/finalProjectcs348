from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Album
from .forms import SongUpdateForm, AlbumForm
from django.db import connection
from .forms import SongForm





def home(request):
    return render(request, "music/home.html")


def redirect_to_album(request):
    return redirect('album_view')

# ORM, retireves Album objects, matches with selected album and changes duration time to mm:ss
def album_view(request):
    albums = Album.objects.all()
    selected_album = request.GET.get("album")

    if selected_album:
        songs = Song.objects.filter(album_id=selected_album).select_related('artist', 'album')
        for song in songs:
            duration_sec = song.duration.total_seconds()
            song.formatted_duration = f"{int(duration_sec // 60)}:{int(duration_sec % 60):02d}"

    else:
        songs = []

    return render(request, "music/album_select.html", {
        "albums": albums,
        "songs": songs,
        "selected_album": int(selected_album) if selected_album else None,
    })


# Stored Procedure, calls AddAlbum in SQL to create new album based on user input

def add_album(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            with connection.cursor() as cursor:
                cursor.callproc("AddAlbum", [
                    data['name'],
                    data['artist'].id,
                    data['release_year']
                ])
            return redirect('album_view')
    else:
        form = AlbumForm()
    return render(request, 'music/add_album.html', {'form': form})


# Stored Procedure, calls DeleteAlbum in SQL based on user input
def delete_album(request, album_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.callproc("DeleteAlbum", [album_id])
        return redirect('album_view')

    album = get_object_or_404(Album, id=album_id)
    return render(request, 'music/delete_album.html', {'album': album})




# Stored Procedure, calls AddSong in mySQL based on userinput
def add_song(request):
    if request.method == 'POST':
        form = SongForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            with connection.cursor() as cursor:
                cursor.callproc("AddSong", [
                    data["title"],
                    data["album"].id,
                    int(data["duration"].total_seconds() * 1_000_000),
                    data["artist"].id,
                    data["genre"],
                    data["explicit"],
                ])
            return redirect('album_view')
    else:
        form = SongForm()
    return render(request, 'music/add_song.html', {'form': form})


# Stored Procedure, calls DeleteSong in mySQL based on song_id from URL
def delete_song(request, song_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.callproc("DeleteSong", [song_id])
        return redirect('album_view')
    song = get_object_or_404(Song, id=song_id)
    return render(request, 'music/delete_song.html', {'song': song})



# Stored Procedure, calls UpdateSong in SQL to update song based on user input

def update_song(request, song_id):
    #error is song is not in database
    song = get_object_or_404(Song, id=song_id)
    if request.method == 'POST':
        form = SongUpdateForm(request.POST, instance=song)
        if form.is_valid():
            data = form.cleaned_data
    #Takes form input and updates song
            with connection.cursor() as cursor:
                cursor.callproc("UpdateSong", [
                    song.id,
                    data["title"],
                    data["album"].id,
                    data["duration"].total_seconds() * 1_000_000,
                    data["artist"].id,
                    data["genre"],
                    data["explicit"]
                ])

            return redirect(reverse('album_view') + f'?album={song.album.id}')
    else:
        form = SongUpdateForm(instance=song)

    return render(request, 'music/update_song.html', {'form': form, 'song': song})



# Prepared Statement, filters songs based on user input
def filter_songs_by_duration(request):
    songs = []
    max_duration = request.GET.get("duration")

    if max_duration:
        try:
            #Convert userinput to microseconds (Database duration)
            minutes, seconds = map(int, max_duration.strip().split(":"))
            max_microseconds = (minutes * 60 + seconds) * 1_000_000

            with connection.cursor() as cursor:
                #SQL query to find songs below threshold
                cursor.execute(
                    """
                    SELECT s.id, s.title, s.duration, a.name AS album_name, ar.name AS artist_name, s.genre, s.explicit
                    FROM music_song s
                    JOIN music_album a ON s.album_id = a.id
                    JOIN music_artist ar ON s.artist_id = ar.id
                    WHERE s.duration < %s
                    ORDER BY ar.name, a.name
                    """,
                    [max_microseconds] #Prevents injection by replacing %s with [parameter]
                )
                rows = cursor.fetchall()

                #Formats songs
                for row in rows:
                    duration_us = row[2]
                    mins = int(duration_us) // 60000000
                    secs = (int(duration_us) // 1000000) % 60
                    songs.append({
                        "id": row[0],
                        "title": row[1],
                        "duration": f"{mins}:{secs:02d}",
                        "album": row[3],
                        "artist": row[4],
                        "genre": row[5],
                        "explicit": row[6],
                    })

        except Exception as e:
            print("Error:", e)

    return render(request, "music/song_filter.html", {
        "songs": songs,
        "max_duration": max_duration,
    })









# Prepared Statement to filter songs based on genre

def filter_songs_by_genre(request):
    songs = []
    genre = request.GET.get("genre")

    if genre:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT s.id, s.title, s.duration, ar.name AS artist_name, a.name AS album_name, s.genre, s.explicit
                FROM music_song s
                JOIN music_artist ar ON s.artist_id = ar.id
                JOIN music_album a ON s.album_id = a.id
                WHERE s.genre = %s
                ORDER BY ar.name, a.name
                """,
                [genre]
            )
            rows = cursor.fetchall()
            for row in rows:
                duration_us = row[2]
                mins = duration_us // 60000000
                secs = (duration_us // 1000000) % 60

                songs.append({
                    "id": row[0],
                    "title": row[1],
                    "duration": f"{mins}:{secs:02d}",
                    "artist": row[3],
                    "album": row[4],
                    "genre": row[5],
                    "explicit": row[6]
                })

    return render(request, "music/filter_by_genre.html", {"songs": songs, "genre": genre})

# Prepared Statement to filter songs based on explicit songs

from .models import Artist, Album

def filter_songs_by_explicit(request):
    songs = []
    is_explicit = request.GET.get("explicit")

    if is_explicit is not None:
        try:
            explicit_bool = bool(int(is_explicit))
        except ValueError:
            explicit_bool = False

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT s.id, s.title, s.duration, ar.name AS artist_name, a.name AS album_name, s.genre, s.explicit
                FROM music_song s
                JOIN music_artist ar ON s.artist_id = ar.id
                JOIN music_album a ON s.album_id = a.id
                WHERE s.explicit = %s
                ORDER BY ar.name, a.name
                """,
                [explicit_bool]
            )
            rows = cursor.fetchall()
            for row in rows:
                duration_us = row[2]
                mins = duration_us // 60000000
                secs = (duration_us // 1000000) % 60

                songs.append({
                    "id": row[0],
                    "title": row[1],
                    "duration": f"{mins}:{secs:02d}",
                    "artist": row[3],
                    "album": row[4],
                    "genre": row[5],
                    "explicit": row[6]
                })

    return render(request, "music/filter_by_explicit.html", {
        "songs": songs,
        "explicit": is_explicit
    })





# Stored Procedure to AddArtist in mySQL

def add_artist(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            with connection.cursor() as cursor:
                cursor.callproc("AddArtist", [name])
            return redirect('add_album')

    return render(request, 'music/add_artist.html')




# Stored Procedure to DeleteArtist in mySQL


def delete_artist(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)

    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.callproc('DeleteArtist', [artist_id])
        return redirect('album_view')

    return render(request, 'music/delete_artist.html', {'artist': artist})



#Select artist objects to delete
def select_artist_to_delete(request):
    artists = Artist.objects.all()
    return render(request, 'music/select_artist_to_delete.html', {'artists': artists})

# Stored procedure by calling DeleteArtist in mySQL
def delete_artist(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.callproc("DeleteArtist", [artist.id])
        return redirect('album_view')
    return render(request, 'music/delete_artist.html', {'artist': artist})

from .models import Song, Playlist, PlaylistEntry

#Creates playlist object when user selects songs from list of songs
def create_playlist(request):
    if request.method == 'POST':
        name = request.POST.get('playlist_name')
        selected_songs = request.POST.getlist('songs')

        if name and selected_songs:
            playlist, _ = Playlist.objects.get_or_create(name=name)
            for song_id in selected_songs:
                try:
                    song = Song.objects.get(id=song_id)
                    PlaylistEntry.objects.get_or_create(playlist=playlist, song=song)
                except Song.DoesNotExist:
                    print(f"Invalid Song ID: {song_id}")
            return redirect('view_playlist', playlist_id=playlist.id)

    all_songs = Song.objects.select_related('album', 'artist').all()

    for song in all_songs:
        duration_sec = song.duration.total_seconds()
        song.formatted_duration = f"{int(duration_sec // 60)}:{int(duration_sec % 60):02d}"

    return render(request, 'music/create_playlist.html', {'songs': all_songs})



# View playlist object with songs
def view_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    entries = PlaylistEntry.objects.filter(playlist=playlist).select_related('song__album', 'song__artist')

    songs = []
    for entry in entries:
        song = entry.song
        duration_us = song.duration.total_seconds() * 1000000 if hasattr(song.duration, 'total_seconds') else song.duration
        mins = int(duration_us) // 60000000
        secs = (int(duration_us) // 1000000) % 60
        formatted_duration = f"{mins}:{secs:02d}"

        songs.append({
            "title": song.title,
            "artist": song.artist.name,
            "album": song.album.name,
            "duration": formatted_duration,
            "genre": song.genre,
            "explicit": song.explicit
        })

    return render(request, 'music/view_playlist.html', {
        'playlist': playlist,
        'songs': songs
    })