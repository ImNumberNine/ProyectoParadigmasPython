
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Autenticación con Spotify API
# Reemplaza 'TU_CLIENT_ID' y 'TU_CLIENT_SECRET' con tus propias credenciales
client_credentials_manager = SpotifyClientCredentials(client_id='ce28579afae84f4281e87ae12658f1c0', client_secret='2dacb21be0814ff2ab4654e0401be8de')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Función para obtener las características de las canciones más populares
def get_top_tracks_features():
    # Asegúrate de reemplazar 'playlist_id' con el ID real de la playlist
    top_tracks = sp.playlist_tracks('1XfO3NSQZo1m6l574HO6dk')
    tracks_info = []

    # Itera sobre las pistas y recoge los datos necesarios
    for track_entry in top_tracks['items']:
        track = track_entry['track']
        track_info = {
            'name': track['name'],
            'artist': ', '.join([artist['name'] for artist in track['artists']]),  # Puede haber más de un artista
            'album': track['album']['name'],  # Si también quieres el nombre del álbum
            'added_at': track_entry['added_at']  # Fecha en que se agregó
        }
        tracks_info.append(track_info)

    # Aquí podrías obtener las características de audio de cada canción usando `sp.audio_features`
    # y luego combinar los datos de `tracks_info` con las características de audio en un DataFrame

    return tracks_info


# Obtener DataFrame con características de las canciones
df_tracks = get_top_tracks_features()

# Procesar y preparar los datos para el modelo
# Aquí seleccionamos solo algunas características para el análisis
features_to_use = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']
df_features = df_tracks[features_to_use]

# Normalizar los datos
# La normalización es importante para que todas las características contribuyan equitativamente al modelo
scaler = StandardScaler()
scaled_features = scaler.fit_transform(df_features)

# Implementar KMeans Clustering
# Este es un algoritmo de clustering que agrupa los datos en 'k' grupos
kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(scaled_features)

# Añadir la columna de clusters al DataFrame original
df_tracks['cluster'] = kmeans.labels_

# Mostrar los resultados
print(df_tracks[['name', 'artist', 'cluster']])

# Este programa agrupa las 10 canciones más populares en 3 categorías basadas en sus características de audio.
