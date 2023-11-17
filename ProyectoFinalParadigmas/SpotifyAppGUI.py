import PySimpleGUI as sg
from SpotifyAppLogica import authenticate_spotify, get_top_tracks_features, process_and_cluster_data

# Configura tus credenciales de Spotify (maneja esto de forma segura, idealmente no en el código)
client_id = 'ce28579afae84f4281e87ae12658f1c0'
client_secret = '2dacb21be0814ff2ab4654e0401be8de'

# Inicializa el cliente de Spotify
sp = authenticate_spotify(client_id, client_secret)

# Define la estructura de la ventana
layout = [
    [sg.Text('Spotify Data Analysis', font=('Helvetica', 16), justification='center', pad=(0,10))],
    [sg.Text('Playlist ID:', size=(15, 1)), sg.InputText(key='PLAYLIST_ID')],
    [sg.Text('Number of Clusters:', size=(15, 1)), sg.Slider(range=(2, 10), default_value=3, size=(20, 15), orientation='horizontal', font=('Helvetica', 12), key='NUM_CLUSTERS')],
    [sg.Button('Load Data', size=(10, 1)), sg.Button('Cluster', size=(10, 1)), sg.Button('Exit', size=(10, 1))],
    [sg.Multiline(size=(70, 20), key='OUTPUT', autoscroll=True, disabled=True)]
]

# Crea la ventana
window = sg.Window('Spotify Playlist Data Clustering', layout)

# Variable para almacenar los datos de la playlist y las características
tracks_info = None
features = None

# Event loop
while True:
    event, values = window.read()
    if event in (None, 'Exit'):
        break
    elif event == 'Load Data':
        playlist_id = values['PLAYLIST_ID']
        try:
            tracks_info, features = get_top_tracks_features(sp, playlist_id)
            window['OUTPUT'].update('Data loaded successfully!\n')
        except Exception as e:
            window['OUTPUT'].update(f"An error occurred: {e}\n")
    elif event == 'Cluster':
        num_clusters = int(values['NUM_CLUSTERS'])
        try:
            if not tracks_info or not features:
                window['OUTPUT'].update('Please load data before clustering.\n')
                continue
            clustering_results = process_and_cluster_data(tracks_info, features, num_clusters)
            window['OUTPUT'].update(clustering_results.to_string(index=False))
        except Exception as e:
            window['OUTPUT'].update(f"An error occurred: {e}\n")

window.close()
