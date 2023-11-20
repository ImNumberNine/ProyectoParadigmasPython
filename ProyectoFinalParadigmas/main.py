import PySimpleGUI as sg
import pandas as pd
from SpotifyAppLogica import (
    authenticate_spotify, get_top_tracks_features, process_and_cluster_data, get_recommendations
)

# Configura tus credenciales de Spotify
client_id = 'ce28579afae84f4281e87ae12658f1c0'
client_secret = '2dacb21be0814ff2ab4654e0401be8de'
sp = authenticate_spotify(client_id, client_secret)

# Define la estructura de la ventana
layout = [
    [sg.Text('Spotify Data Analysis', font=('Helvetica', 16), justification='center')],
    [sg.Text('Playlist ID:'), sg.InputText(key='PLAYLIST_ID')],
    [sg.Text('Number of Clusters:'), sg.Slider(range=(2, 10), orientation='h', size=(34, 20), default_value=3, key='NUM_CLUSTERS')],
    [sg.Button('Load Data'), sg.Button('Cluster'), sg.Button('Exit')],
    [sg.Table(values=[], headings=['ID', 'Name', 'Artist', 'Cluster'], auto_size_columns=True, display_row_numbers=False, key='TABLE')],
    [sg.Text('Song ID for Recommendations:'), sg.InputText(key='SONG_ID')],
    [sg.Button('Get Recommendations'), sg.Listbox(values=[], size=(60, 4), key='RECOMMENDATIONS')]
]

# Crea la ventana
window = sg.Window('Spotify Data Analysis', layout)

# Inicializa las variables para almacenar los datos de la playlist y las características
tracks_info, features, clustered_data = None, None, pd.DataFrame()

# Event loop para procesar "eventos" y obtener los "valores" de las entradas
while True:
    event, values = window.read()
    if event in (None, 'Exit'):
        break
    elif event == 'Load Data':
        playlist_id = values['PLAYLIST_ID']
        sp = authenticate_spotify(client_id, client_secret)
        tracks_info, features = get_top_tracks_features(sp, playlist_id)
        # Actualiza la tabla con los datos cargados, incluyendo el ID de la canción
        table_data = [[track['id'], track['name'], track['artist']] for track in tracks_info]
        window['TABLE'].update(values=table_data)
    elif event == 'Cluster':
        num_clusters = values['NUM_CLUSTERS']
        if tracks_info and features:
            clustered_data = process_and_cluster_data(tracks_info, features, num_clusters)
            # Actualiza la tabla con los resultados del clustering, incluyendo el ID de la canción
            table_data = [[row['id'], row['name'], row['artist'], row['cluster']] for index, row in clustered_data.iterrows()]
            window['TABLE'].update(values=table_data)
    elif event == 'Get Recommendations':
        song_id = values['SONG_ID']
        if not clustered_data.empty and song_id:
            recommended_songs = get_recommendations(clustered_data, song_id)
            # Convierte las recomendaciones en una lista para mostrar en la GUI
            recommendations_to_show = [' - '.join([row['id'], row['name'], row['artist']]) for index, row in recommended_songs.iterrows()]
            window['RECOMMENDATIONS'].update(recommendations_to_show)

window.close()
