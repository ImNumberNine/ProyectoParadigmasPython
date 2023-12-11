import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def authenticate_spotify(client_id, client_secret):
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_top_tracks_features(sp, playlist_id):
    try:
        top_tracks = sp.playlist_tracks(playlist_id)
        tracks_info = []
        track_ids = []

        for track_entry in top_tracks['items']:
            track = track_entry['track']
            track_ids.append(track['id'])
            tracks_info.append({
                'id': track['id'],
                'name': track['name'],
                'artist': ', '.join([artist['name'] for artist in track['artists']])
            })

        features = sp.audio_features(track_ids)
        for i, feature in enumerate(features):
            if feature:  # Verifica si existe la característica
                tracks_info[i].update(feature)

        return pd.DataFrame(tracks_info)  # Devuelve un DataFrame
    except spotipy.SpotifyException as e:
        # Aquí puedes decidir si quieres imprimir el error o lanzar una excepción personalizada
        print(f"Error retrieving track features: {e}")
        # O lanzar una excepción para ser capturada por la llamada superior
        raise

def process_and_cluster_data(df, num_clusters):
    features_to_use = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']
    df_features = df[features_to_use]
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df_features)
    kmeans = KMeans(n_clusters=num_clusters, n_init=10, random_state=42)

    kmeans.fit(scaled_features)
    df['cluster'] = kmeans.labels_
    return df

def get_recommendations(clustered_data, song_id, num_recommendations=5):
    song_cluster = clustered_data[clustered_data['id'] == song_id]['cluster'].values[0]
    same_cluster_songs = clustered_data[clustered_data['cluster'] == song_cluster]
    recommendations = same_cluster_songs[same_cluster_songs['id'] != song_id]
    if len(recommendations) > num_recommendations:
        recommendations = recommendations.sample(n=num_recommendations)
    return recommendations

def export_cluster_results_to_csv(clustered_data, file_path):
    try:
        clustered_data.to_csv(file_path, index=False)
    except Exception as e:
        print(f"Error exporting to CSV: {e}")

def export_cluster_results_to_excel(clustered_data, file_path):
    try:
        clustered_data.to_excel(file_path, index=False)
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
