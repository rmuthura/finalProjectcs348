from django import template

register = template.Library()

@register.filter
def get_artist_id(albums, selected_album_id):
    try:
        album = albums.get(id=selected_album_id)
        return album.artist.id
    except:
        return None
