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

class SpotifyAppGUI:
    # Aquí se define la estructura de la GUI (secciones de la interfaz
    def __init__(self):
        self.client_id = 'ce28579afae84f4281e87ae12658f1c0'
        self.client_secret = '2dacb21be0814ff2ab4654e0401be8de'
        self.sp = authenticate_spotify(self.client_id, self.client_secret)
        self.df = pd.DataFrame()
        self.clustered_data = pd.DataFrame()
        sg.theme('DarkTeal9')
        self.window = sg.Window('Spotify Data Analysis', self.create_layout(), resizable=True)


    def create_layout(self):
        # Definición de las secciones de la interfaz
        load_section = [
            [sg.Text('Playlist ID:', size=(15, 1)), sg.InputText(key='PLAYLIST_ID')],
            [sg.Button('Load Data', size=(10, 1))]
        ]

        cluster_section = [
            [sg.Text('Number of Clusters:', size=(15, 1)),
             sg.Slider(range=(2, 10), orientation='h', size=(34, 20), default_value=3, key='NUM_CLUSTERS')],
            [sg.Button('Cluster', size=(10, 1))],
            [sg.Table(values=[], headings=['ID', 'Name', 'Artist', 'Cluster'], auto_size_columns=True,
                      display_row_numbers=False, key='TABLE', size=(None, 10))]
        ]

        recommendations_section = [
            [sg.Text('Song ID for Recommendations:', size=(25, 1)), sg.InputText(key='SONG_ID')],
            [sg.Button('Get Recommendations', size=(15, 1)), sg.Listbox(values=[], size=(60, 6), key='RECOMMENDATIONS')]
        ]

        export_section = [
            [sg.Button('Export to CSV', size=(15, 1)), sg.Button('Export to Excel', size=(15, 1))]
        ]

        eda_section = [
            [sg.Text('Select Feature for EDA:'), sg.Combo(
                ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence'],
                key='EDA_FEATURE')],
            [sg.Button('Show Stats', size=(10, 1)), sg.Button('Show Plot', size=(10, 1))],
            [sg.Image(key='EDA_PLOT')],
            [sg.Multiline(key='EDA_STATS', size=(60, 5), disabled=True)]
        ]

        layout = [
            [sg.Text('Spotify Data Analysis', font=('Helvetica', 16), justification='center', pad=(0, 10))],
            [sg.Frame('Load Data', load_section, font='Any 12', title_color='yellow')],
            [sg.Frame('Cluster and Results', cluster_section, font='Any 12', title_color='yellow')],
            [sg.Frame('Recommendations', recommendations_section, font='Any 12', title_color='yellow')],
            [sg.Frame('Export', export_section, font='Any 12', title_color='yellow')],
            [sg.Frame('Exploratory Data Analysis', eda_section, font='Any 12', title_color='yellow')]
        ]
        return layout

    def convert_plot_to_image(self, figure):
        with io.BytesIO() as output:
            figure.savefig(output, format="PNG")
            plt.close(figure)
            return base64.b64encode(output.getvalue())
        pass

    def load_data(self, playlist_id):
        self.df = get_top_tracks_features(self.sp, playlist_id)

    def perform_clustering(self):
        num_clusters = int(self.values['NUM_CLUSTERS'])
        self.clustered_data = process_and_cluster_data(self.df, num_clusters)
        return [[row['id'], row['name'], row['artist'], row['cluster']] for index, row in
                self.clustered_data.iterrows()]

    def get_recommendations(self, song_id):
        recommended_songs = get_recommendations(self.clustered_data, song_id)
        return [' - '.join([row['id'], row['name'], row['artist']]) for index, row in recommended_songs.iterrows()]

    def export_to_csv(self, file_path):
        export_cluster_results_to_csv(self.clustered_data, file_path)

    def export_to_excel(self, file_path):
        export_cluster_results_to_excel(self.clustered_data, file_path)

    def show_stats(self, selected_feature):
        return self.df[selected_feature].describe().to_string()

    def show_plot(self, selected_feature):
        fig = plt.figure()
        sns.histplot(self.df[selected_feature], kde=True)
        return self.convert_plot_to_image(fig)

    def run(self):
        while True:
            event, self.values = self.window.read()
            if event in (None, 'Exit'):
                break

            if event == 'Load Data':
                self.load_data(self.values['PLAYLIST_ID'])
                table_data = [[track['id'], track['name'], track['artist']] for track in self.df.to_dict('records')]
                self.window['TABLE'].update(values=table_data)

            elif event == 'Cluster':
                if not self.df.empty:
                    table_data = self.perform_clustering()
                    self.window['TABLE'].update(values=table_data)

            elif event == 'Get Recommendations':
                if not self.clustered_data.empty:
                    recommendations_to_show = self.get_recommendations(self.values['SONG_ID'])
                    self.window['RECOMMENDATIONS'].update(recommendations_to_show)

            elif event == 'Export to CSV':
                if not self.clustered_data.empty:
                    file_path = sg.popup_get_file('Choose a CSV file to save the results', save_as=True,
                                                  default_extension=".csv")
                    self.export_to_csv(file_path)

            elif event == 'Export to Excel':
                if not self.clustered_data.empty:
                    file_path = sg.popup_get_file('Choose an Excel file to save the results', save_as=True,
                                                  default_extension=".xlsx")
                    self.export_to_excel(file_path)

            elif event == 'Show Stats':
                if not self.df.empty:
                    stats = self.show_stats(self.values['EDA_FEATURE'])
                    self.window['EDA_STATS'].update(stats)

            elif event == 'Show Plot':
                if not self.df.empty:
                    image = self.show_plot(self.values['EDA_FEATURE'])
                    self.window['EDA_PLOT'].update(data=image)

        self.window.close()