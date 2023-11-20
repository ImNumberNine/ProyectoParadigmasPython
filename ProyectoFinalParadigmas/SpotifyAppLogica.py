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

    for track_entry in top_tracks['items']:
        track = track_entry['track']
        track_ids.append(track['id'])
        tracks_info.append({
            'id': track['id'],  # Este es el ID de la canción que Spotify asigna
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
    kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
    kmeans.fit(scaled_features)

    # Añadir la columna de clusters al DataFrame original
    df['cluster'] = kmeans.labels_

    return df[['id', 'name', 'artist', 'cluster']]



def get_recommendations(clustered_data, song_id, num_recommendations=5):
    """
    Genera recomendaciones de canciones basadas en el cluster de una canción específica.

    :param clustered_data: DataFrame con las canciones y sus clusters.
    :param song_id: El ID de la canción que el usuario ha seleccionado.
    :param num_recommendations: Número de recomendaciones a generar.
    :return: DataFrame con las canciones recomendadas.
    """
    # Encuentra el cluster de la canción seleccionada
    song_cluster = clustered_data[clustered_data['id'] == song_id]['cluster'].values[0]

    # Filtra canciones del mismo cluster
    same_cluster_songs = clustered_data[clustered_data['cluster'] == song_cluster]

    # Elimina la canción seleccionada de las recomendaciones
    recommendations = same_cluster_songs[same_cluster_songs['id'] != song_id]

    # Si hay demasiadas recomendaciones, devuelve una muestra aleatoria
    if len(recommendations) > num_recommendations:
        recommendations = recommendations.sample(n=num_recommendations)

    return recommendations[['name', 'artist', 'id', 'cluster']]


import pandas as pd

def export_cluster_results_to_csv(clustered_data, file_path):
    """
    Exporta los resultados del clustering a un archivo CSV.

    :param clustered_data: DataFrame con los resultados del clustering.
    :param file_path: Ruta del archivo CSV de destino.
    """
    try:
        clustered_data.to_csv(file_path, index=False)
    except Exception as e:
        print(f"Error exporting to CSV: {e}")

def export_cluster_results_to_excel(clustered_data, file_path):
    """
    Exporta los resultados del clustering a un archivo Excel.

    :param clustered_data: DataFrame con los resultados del clustering.
    :param file_path: Ruta del archivo Excel de destino.
    """
    try:
        clustered_data.to_excel(file_path, index=False)
    except Exception as e:
        print(f"Error exporting to Excel: {e}")

