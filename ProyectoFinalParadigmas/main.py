import matplotlib.pyplot as plt
import io
import seaborn as sns
import base64
from PIL import Image
import PySimpleGUI as sg
import pandas as pd
from SpotifyAppLogica import (
    authenticate_spotify, get_top_tracks_features, process_and_cluster_data, get_recommendations,
    export_cluster_results_to_csv, export_cluster_results_to_excel
)

# Configuración de las credenciales de Spotify
client_id = 'ce28579afae84f4281e87ae12658f1c0'
client_secret = '2dacb21be0814ff2ab4654e0401be8de'
sp = authenticate_spotify(client_id, client_secret)

# DataFrame para almacenar datos
df = pd.DataFrame()

# Configuración del tema para la interfaz gráfica
sg.theme('DarkTeal9')

# Definición de las secciones de la interfaz
load_section = [
    [sg.Text('Playlist ID:', size=(15, 1)), sg.InputText(key='PLAYLIST_ID')],
    [sg.Button('Load Data', size=(10, 1))]
]

cluster_section = [
    [sg.Text('Number of Clusters:', size=(15, 1)), sg.Slider(range=(2, 10), orientation='h', size=(34, 20), default_value=3, key='NUM_CLUSTERS')],
    [sg.Button('Cluster', size=(10, 1))],
    [sg.Table(values=[], headings=['ID', 'Name', 'Artist', 'Cluster'], auto_size_columns=True, display_row_numbers=False, key='TABLE', size=(None, 10))]
]

recommendations_section = [
    [sg.Text('Song ID for Recommendations:', size=(25, 1)), sg.InputText(key='SONG_ID')],
    [sg.Button('Get Recommendations', size=(15, 1)), sg.Listbox(values=[], size=(60, 6), key='RECOMMENDATIONS')]
]

export_section = [
    [sg.Button('Export to CSV', size=(15, 1)), sg.Button('Export to Excel', size=(15, 1))]
]

eda_section = [
    [sg.Text('Select Feature for EDA:'), sg.Combo(['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence'], key='EDA_FEATURE')],
    [sg.Button('Show Stats', size=(10, 1)), sg.Button('Show Plot', size=(10, 1))],
    [sg.Image(key='EDA_PLOT')],
    [sg.Multiline(key='EDA_STATS', size=(60, 5), disabled=True)]
]

# Combinación de todas las secciones en el layout principal
layout = [
    [sg.Text('Spotify Data Analysis', font=('Helvetica', 16), justification='center', pad=(0,10))],
    [sg.Frame('Load Data', load_section, font='Any 12', title_color='yellow')],
    [sg.Frame('Cluster and Results', cluster_section, font='Any 12', title_color='yellow')],
    [sg.Frame('Recommendations', recommendations_section, font='Any 12', title_color='yellow')],
    [sg.Frame('Export', export_section, font='Any 12', title_color='yellow')],
    [sg.Frame('Exploratory Data Analysis', eda_section, font='Any 12', title_color='yellow')]
]

# Creación de la ventana
window = sg.Window('Spotify Data Analysis', layout, resizable=True)

# Función para convertir un gráfico de matplotlib en una imagen para PySimpleGUI
def convert_plot_to_image(figure):
    with io.BytesIO() as output:
        figure.savefig(output, format="PNG")
        plt.close(figure)
        return base64.b64encode(output.getvalue())

# Bucle de eventos para manejar la interacción del usuario
while True:
    event, values = window.read()
    if event in (None, 'Exit'):
        break

    if event == 'Load Data':
        playlist_id = values['PLAYLIST_ID']
        df = get_top_tracks_features(sp, playlist_id)

    elif event == 'Cluster':
        if not df.empty:
            num_clusters = int(values['NUM_CLUSTERS'])
            clustered_data = process_and_cluster_data(df, num_clusters)
            table_data = [[row['id'], row['name'], row['artist'], row['cluster']] for index, row in clustered_data.iterrows()]
            window['TABLE'].update(values=table_data)

    elif event == 'Get Recommendations':
        if not clustered_data.empty:
            song_id = values['SONG_ID']
            recommended_songs = get_recommendations(clustered_data, song_id)
            recommendations_to_show = [' - '.join([row['id'], row['name'], row['artist']]) for index, row in recommended_songs.iterrows()]
            window['RECOMMENDATIONS'].update(recommendations_to_show)

    elif event == 'Export to CSV':
        if not clustered_data.empty:
            file_path = sg.popup_get_file('Choose a CSV file to save the results', save_as=True, default_extension=".csv")
            export_cluster_results_to_csv(clustered_data, file_path)

    elif event == 'Export to Excel':
        if not clustered_data.empty:
            file_path = sg.popup_get_file('Choose an Excel file to save the results', save_as=True, default_extension=".xlsx")
            export_cluster_results_to_excel(clustered_data, file_path)

    elif event == 'Show Stats':
        if not df.empty:
            selected_feature = values['EDA_FEATURE']
            stats = df[selected_feature].describe().to_string()
            window['EDA_STATS'].update(stats)

    elif event == 'Show Plot':
        if not df.empty:
            selected_feature = values['EDA_FEATURE']
            fig = plt.figure()
            sns.histplot(df[selected_feature], kde=True)
            image = convert_plot_to_image(fig)
            window['EDA_PLOT'].update(data=image)

window.close()
