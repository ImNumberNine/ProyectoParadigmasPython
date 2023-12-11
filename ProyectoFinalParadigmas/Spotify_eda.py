import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from SpotifyAppLogica import authenticate_spotify, get_top_tracks_features
import numpy as np
from sklearn.decomposition import PCA

# Configura tus credenciales de Spotify
client_id = 'ce28579afae84f4281e87ae12658f1c0'
client_secret = '2dacb21be0814ff2ab4654e0401be8de'
sp = authenticate_spotify(client_id, client_secret)

# Función para obtener datos de playlists específicas
def get_data_from_playlists(sp, playlist_ids):
    all_tracks_info = []
    for playlist_id in playlist_ids:
        tracks_info, _ = get_top_tracks_features(sp, playlist_id)
        all_tracks_info.extend(tracks_info)
    return all_tracks_info

# IDs de playlists de géneros populares y math rock japonés
# Debes reemplazar estos con IDs reales de playlists de Spotify
playlist_ids = {
    'Pop': 'id_playlist_pop',
    'Rock': 'id_playlist_rock',
    'Math Rock Japonés': 'id_playlist_math_rock_japones',
    # ... otros géneros ...
}

# Obtener datos
all_genres_data = {}
for genre, playlist_id in playlist_ids.items():
    all_genres_data[genre] = get_data_from_playlists(sp, [playlist_id])

# Convertir a DataFrame
df = pd.DataFrame()
for genre, data in all_genres_data.items():
    temp_df = pd.DataFrame(data)
    temp_df['genre'] = genre
    df = df.append(temp_df)

# Análisis Exploratorio de Datos (EDA)

# Distribución de características por género
features = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence']
for feature in features:
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='genre', y=feature, data=df)
    plt.title(f'Distribución de {feature} por Género')
    plt.xlabel('Género')
    plt.ylabel(feature.capitalize())
    plt.xticks(rotation=45)
    plt.show()

# Correlaciones entre características
plt.figure(figsize=(10, 8))
sns.heatmap(df[features].corr(), annot=True, fmt=".2f")
plt.title('Matriz de Correlación de Características')
plt.show()

# Análisis estadístico por género
for genre in df['genre'].unique():
    print(f"Estadísticas de {genre}:")
    print(df[df['genre'] == genre][features].describe())
    print("\n")

# Visualizaciones de distribuciones por género
for feature in features:
    plt.figure(figsize=(10, 6))
    for genre in df['genre'].unique():
        sns.kdeplot(df[df['genre'] == genre][feature], label=genre)
    plt.title(f'Distribución de {feature} por Género')
    plt.legend()
    plt.show()

# Preparación para PCA
df_pca = pd.get_dummies(df[features + ['genre']], columns=['genre'])
pca = PCA(n_components=2)
components = pca.fit_transform(df_pca)

# Visualización de PCA
plt.figure(figsize=(10, 6))
for genre in df['genre'].unique():
    idx = df['genre'] == genre
    plt.scatter(components[idx, 0], components[idx, 1], label=genre)
plt.title('Análisis de Componentes Principales (PCA) por Género')
plt.xlabel('Componente Principal 1')
plt.ylabel('Componente Principal 2')
plt.legend()
plt.show()

