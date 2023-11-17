import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# Autenticación con Spotify API
def authenticate_spotify(client_id, client_secret):
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# Función para obtener las características de las canciones más populares
def get_top_tracks_features(sp, playlist_id):
    top_tracks = sp.playlist_tracks(playlist_id)
    tracks_info = []
    track_ids = []

    # Itera sobre las pistas y recoge los datos necesarios
    for track_entry in top_tracks['items']:
        track = track_entry['track']
        track_ids.append(track['id'])
        tracks_info.append({
            'id': track['id'],
            'name': track['name'],
            'artist': ', '.join([artist['name'] for artist in track['artists']])
        })

    features = sp.audio_features(track_ids)
    return tracks_info, features


# Función que procesa los datos y aplica el clustering
def process_and_cluster_data(tracks_info, features, num_clusters):
    df_tracks_info = pd.DataFrame(tracks_info)
    df_features = pd.DataFrame(features)

    # Fusionar información de pistas y características en un DataFrame
    df = pd.merge(df_tracks_info, df_features, on='id')

    # Seleccionar solo algunas características para el análisis
    features_to_use = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness',
                       'valence']
    df_selected_features = df[features_to_use]

    # Normalizar los datos
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df_selected_features)

    # Implementar KMeans Clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(scaled_features)

    # Añadir la columna de clusters al DataFrame original
    df['cluster'] = kmeans.labels_

    return df[['name', 'artist', 'cluster']]

'''
# Ejemplo de cómo se llamarían estas funciones:
if __name__ == "__main__":
    sp = authenticate_spotify('ce28579afae84f4281e87ae12658f1c0', '2dacb21be0814ff2ab4654e0401be8de')
    tracks_info, features = get_top_tracks_features(sp, '1XfO3NSQZo1m6l574HO6dk')
    clustered_data = process_and_cluster_data(tracks_info, features, 3)
    print(clustered_data)
'''