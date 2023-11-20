import matplotlib.pyplot as plt
import io
import base64
from PIL import Image
import PySimpleGUI as sg
import pandas as pd
from SpotifyAppLogica import (
    authenticate_spotify, get_top_tracks_features, process_and_cluster_data, get_recommendations,
    export_cluster_results_to_csv, export_cluster_results_to_excel
)

# Configura tus credenciales de Spotify
client_id = 'ce28579afae84f4281e87ae12658f1c0'
client_secret = '2dacb21be0814ff2ab4654e0401be8de'
sp = authenticate_spotify(client_id, client_secret)

# Establece un tema para la GUI
sg.theme('DarkTeal9')

# Estructura de la sección de carga de datos
load_section = [
    [sg.Text('Playlist ID:', size=(15, 1)), sg.InputText(key='PLAYLIST_ID')],
    [sg.Button('Load Data', size=(10, 1))]
]

# Estructura de la sección de clustering y visualización de resultados
cluster_section = [
    [sg.Text('Number of Clusters:', size=(15, 1)), sg.Slider(range=(2, 10), orientation='h', size=(34, 20), default_value=3, key='NUM_CLUSTERS')],
    [sg.Button('Cluster', size=(10, 1))],
    [sg.Table(values=[], headings=['ID', 'Name', 'Artist', 'Cluster'], auto_size_columns=True, display_row_numbers=False, key='TABLE', size=(None, 10))]
]

# Estructura de la sección de recomendaciones
recommendations_section = [
    [sg.Text('Song ID for Recommendations:', size=(25, 1)), sg.InputText(key='SONG_ID')],
    [sg.Button('Get Recommendations', size=(15, 1)), sg.Listbox(values=[], size=(60, 6), key='RECOMMENDATIONS')]
]

# Estructura de la sección de exportación
export_section = [
    [sg.Button('Export to CSV', size=(15, 1)), sg.Button('Export to Excel', size=(15, 1))]
]

# Layout principal que combina todas las secciones
layout = [
    [sg.Text('Spotify Data Analysis', font=('Helvetica', 16), justification='center', pad=(0,10))],
    [sg.Frame('Load Data', load_section, font='Any 12', title_color='yellow')],
    [sg.Frame('Cluster and Results', cluster_section, font='Any 12', title_color='yellow')],
    [sg.Frame('Recommendations', recommendations_section, font='Any 12', title_color='yellow')],
    [sg.Frame('Export', export_section, font='Any 12', title_color='yellow')]
]

# Crea la ventana
window = sg.Window('Spotify Data Analysis', layout, resizable=True)

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
        clustered_data = pd.DataFrame()  # Actualiza clustered_data

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
    elif event == 'Export to CSV':
        if not clustered_data.empty:
            file_path = sg.popup_get_file('Choose a CSV file to save the results', save_as=True, default_extension=".csv")
            if file_path:
                export_cluster_results_to_csv(clustered_data, file_path)
    elif event == 'Export to Excel':
        if not clustered_data.empty:
            file_path = sg.popup_get_file('Choose an Excel file to save the results', save_as=True, default_extension=".xlsx")
            if file_path:
                export_cluster_results_to_excel(clustered_data, file_path)

window.close()

