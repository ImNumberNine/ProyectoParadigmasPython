import PySimpleGUI as sg
from SpotifyAppLogica import authenticate_spotify, get_top_tracks_features, process_and_cluster_data


layout = [
    [sg.Text('Spotify Data Analysis', font=('Helvetica', 16), justification='center')],
    [sg.Text('Playlist ID:'), sg.InputText(key='PLAYLIST_ID')],
    [sg.Text('Number of Clusters:'), sg.Slider(range=(2, 10), orientation='h', size=(34, 20), default_value=3, key='NUM_CLUSTERS')],
    [sg.Button('Load Data'), sg.Button('Cluster'), sg.Button('Exit')],
    [sg.Table(values=[], headings=['Name', 'Artist', 'Cluster'], auto_size_columns=True, display_row_numbers=False, key='TABLE')]
]


window = sg.Window('Spotify Data Analysis', layout)
# Variables para almacenar los datos de la playlist y las características
tracks_info = None
features = None
table_data = []  # Inicializa la variable table_data

# Event loop para procesar "eventos" y obtener los "valores" de las entradas
while True:
    event, values = window.read()
    if event in (None, 'Exit'):
        break
    elif event == 'Load Data':
        playlist_id = values['PLAYLIST_ID']
        try:
            sp = authenticate_spotify('tu_client_id', 'tu_client_secret')
            tracks_info, features = get_top_tracks_features(sp, playlist_id)
            # Prepara los datos para la tabla, esto podría ser una lista de listas que representa cada fila
            table_data = [[track['name'], track['artist']] for track in tracks_info]
            window['TABLE'].update(values=table_data)  # Actualiza la tabla con los datos cargados
        except Exception as e:
            sg.Popup(f"An error occurred: {e}")
    elif event == 'Cluster':
        num_clusters = values['NUM_CLUSTERS']
        try:
            if not tracks_info or not features:
                sg.Popup('Please load data before clustering.')
                continue
            # Realiza el clustering y luego prepara los datos para actualizar la tabla
            clustered_data = process_and_cluster_data(tracks_info, features, num_clusters)
            table_data = [[row['name'], row['artist'], row['cluster']] for index, row in clustered_data.iterrows()]
            window['TABLE'].update(values=table_data)  # Actualiza la tabla con los resultados del clustering
        except Exception as e:
            sg.Popup(f"An error occurred: {e}")

window.close()