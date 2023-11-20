import PySimpleGUI as sg
import pandas as pd
from SpotifyAppLogica import (
    authenticate_spotify,
    get_top_tracks_features,
    process_and_cluster_data,
    get_recommendations,
    export_cluster_results_to_csv,
    export_cluster_results_to_excel
)

# Define la estructura de la ventana
layout = [
    [sg.Text('Spotify Data Analysis', font=('Helvetica', 16), justification='center')],
    [sg.Text('Playlist ID:'), sg.InputText(key='PLAYLIST_ID')],
    [sg.Text('Number of Clusters:'), sg.Slider(range=(2, 10), orientation='h', size=(34, 20), default_value=3, key='NUM_CLUSTERS')],
    [sg.Button('Load Data'), sg.Button('Cluster'), sg.Button('Export to CSV'), sg.Button('Export to Excel'), sg.Button('Exit')],
    [sg.Table(values=[], headings=['ID', 'Name', 'Artist', 'Cluster'], auto_size_columns=True,
              display_row_numbers=False, key='TABLE')],
    [sg.Text('Song ID for Recommendations:'), sg.InputText(key='SONG_ID')],
    [sg.Button('Get Recommendations'), sg.Listbox(values=[], size=(60, 4), key='RECOMMENDATIONS')]
]

# Configura tus credenciales de Spotify (maneja esto de forma segura, idealmente no en el código)
client_id = 'ce28579afae84f4281e87ae12658f1c0'
client_secret = '2dacb21be0814ff2ab4654e0401be8de'

# Inicializa el cliente de Spotify
sp = authenticate_spotify(client_id, client_secret)

# Crea la ventana
window = sg.Window('Spotify Playlist Data Clustering', layout)

# Variable para almacenar los datos de la playlist y las características
tracks_info = None
features = None

# Inicialmente, clustered_data está vacío hasta que se realiza el clustering
clustered_data = pd.DataFrame()

# Event loop
while True:
    event, values = window.read()
    if event in (None, 'Exit'):
        break

    elif event == 'Load Data':
        playlist_id = values['PLAYLIST_ID']
        try:
            tracks_info, features = get_top_tracks_features(sp, playlist_id)
            window['TABLE'].update(values=[])  # Limpiar la tabla al cargar nuevos datos
            window['RECOMMENDATIONS'].update(values=[])  # Limpiar las recomendaciones al cargar nuevos datos
        except Exception as e:
            sg.popup(f"An error occurred: {e}")

    elif event == 'Cluster':
        num_clusters = int(values['NUM_CLUSTERS'])  # Convierte a entero
        try:
            if tracks_info and features:  # Asegúrate de que se hayan cargado los datos
                # Realiza el clustering
                clustering_results = process_and_cluster_data(tracks_info, features, num_clusters)
                # Actualiza la tabla con los resultados del clustering
                table_data = [[row['id'], row['name'], row['artist'], row['cluster']] for index, row in
                              clustering_results.iterrows()]
                window['TABLE'].update(values=table_data)
                clustered_data = clustering_results  # Actualiza clustered_data para su uso en otras funciones
            else:
                sg.popup('Please load data before clustering.')
        except Exception as e:
            sg.popup(f"An error occurred: {e}")

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

    elif event == 'Get Recommendations':
        try:
            # Asume que 'clustered_data' es el DataFrame retornado por 'process_and_cluster_data'
            song_id = values['SONG_ID']
            if not clustered_data.empty and song_id:
                # Obtiene recomendaciones
                recommended_songs = get_recommendations(clustered_data, song_id)
                # Actualiza la lista de recomendaciones en la GUI
                recommendations_to_show = [' - '.join([row['name'], row['artist']]) for index, row in
                                           recommended_songs.iterrows()]
                window['RECOMMENDATIONS'].update(values=recommendations_to_show)
            else:
                sg.popup('Please perform clustering and enter a valid song ID before getting recommendations.')
        except Exception as e:
            sg.popup(f"An error occurred: {e}")

window.close()

