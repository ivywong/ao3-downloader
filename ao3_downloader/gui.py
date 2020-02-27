import PySimpleGUI as sg

import pathlib
import sys
from multiprocessing import Process

import downloader

# hacky debug window for showing progress
print = sg.Print
downloader.print = sg.Print

class Gui():
    def __init__(self):
        sg.theme('SystemDefault')   # Add a touch of color

        user_home = str(pathlib.Path.home())

        # All the stuff inside your window.
        layout = [  [sg.Text('Ao3 Download URL', size=(20, 1)), sg.InputText('https://archiveofourown.org/series/XXXXXX')],
                    [sg.Text('Download Destination', size=(20,1)), sg.InputText(user_home), sg.FolderBrowse(initial_folder=user_home)],
                    [sg.Text('File format', size=(20, 1)), sg.Combo(['azw3', 'mobi', 'epub', 'pdf', 'html'], default_value='epub')],
#                    [sg.Text('Output:')],
#                    [sg.Output(size=(88, 20), key='Output')],
                    [sg.Button('Download'), sg.Button('Cancel')] ]

        # Create the Window
        self.window = sg.Window('AO3 Downloader', layout)

def start_download(series_url, download_path, file_format):
    proc = Process(target=downloader.download_series, args=(series_url, download_path, file_format))
    proc.start()
    proc.join()

if __name__ == '__main__':
    gui = Gui()
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = gui.window.read()
        if event in (None, 'Cancel'):   # if user closes window or clicks cancel
            break

        gui.window['Browse'].update(disabled=True)
        gui.window['Download'].update(disabled=True)
        print('You entered ', values)

        series_url = values[0]
        download_path = pathlib.Path(values[1])
        file_format = values[2]

        print("Series URL: {}".format(series_url))
        print("Download destination: {}".format(download_path))
        print("File format: {}".format(file_format))

        if series_url and download_path:
            try:
                downloader.download_series(series_url, download_path, file_format)
            except ValueError as e:
                print(e)
                sys.exit(1)

        print("done.")

        gui.window['Browse'].update(disabled=False)
        gui.window['Download'].update(disabled=False)

    gui.window.close()
