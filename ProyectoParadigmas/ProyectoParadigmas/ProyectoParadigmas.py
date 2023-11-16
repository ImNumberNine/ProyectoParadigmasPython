
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Autenticaci�n con Spotify API
# Reemplaza 'TU_CLIENT_ID' y 'TU_CLIENT_SECRET' con tus propias credenciales
client_credentials_manager = SpotifyClientCredentials(client_id='ce28579afae84f4281e87ae12658f1c0', client_secret='2dacb21be0814ff2ab4654e0401be8de')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Funci�n para obtener las caracter�sticas de las canciones m�s populares
def get_top_tracks_features():
    # Obtener las 10 canciones m�s populares (top tracks) de Spotify
    top_tracks = sp.playlist_tracks('playlist_id_con_top_10') # Reemplaza con el ID de la playlist
    track_ids = [track['track']['id'] for track in top_tracks['items']]

    # Obtener caracter�sticas de audio para cada canci�n
    features = sp.audio_features(track_ids)
    return pd.DataFrame(features)

# Obtener DataFrame con caracter�sticas de las canciones
df_tracks = get_top_tracks_features()

# Procesar y preparar los datos para el modelo
# Aqu� seleccionamos solo algunas caracter�sticas para el an�lisis
features_to_use = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']
df_features = df_tracks[features_to_use]

# Normalizar los datos
# La normalizaci�n es importante para que todas las caracter�sticas contribuyan equitativamente al modelo
scaler = StandardScaler()
scaled_features = scaler.fit_transform(df_features)

# Implementar KMeans Clustering
# Este es un algoritmo de clustering que agrupa los datos en 'k' grupos
kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(scaled_features)

# A�adir la columna de clusters al DataFrame original
df_tracks['cluster'] = kmeans.labels_

# Mostrar los resultados
print(df_tracks[['name', 'artist', 'cluster']])

# Este programa agrupa las 10 canciones m�s populares en 3 categor�as basadas en sus caracter�sticas de audio.
