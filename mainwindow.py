import threading
import PySimpleGUI as sg
import os.path
import re
from imagescompress import ImagesCompress


class GUI:

    @property  # ReadOnly
    def window(self):
        return self.__window

    @window.setter  # Setter
    def window(self, value):
        if not self.__window:
            self.__window = value

    min_size = 0
    max_size = 5000
    compress_quality = 85
    convert_mode = 0
    compress_mode = 0
    images_list = []
    folder: str
    progress = False
    counter = 0
    progress_el: int

    def listImages(self, folder, minSize=0, maxSize=5000):
        imageList = []
        for root, dirs, files in os.walk(folder):
            for file in files:
                frst_regex_res = re.match(
                    re.compile('(.*jpg$)|(.*jpeg$)|(.*gif$)|(.*png$)|(.*webp$)|(.*tiff)', re.IGNORECASE), file)

                # paths = get_path(root)
                current_root = root.replace('\\', '/')

                if frst_regex_res:
                    file_size = round(os.stat(current_root + "/" + file).st_size / 1024, 3)
                    # print(file_size)
                    # print(file)
                    # new_file_name : str
                    # image_format : str

                    if file_size <= maxSize and file_size >= minSize or maxSize == 0 and minSize == 0:
                        imageList.append([file, current_root, file_size])
                    elif (maxSize == 0):
                        imageList.append([file, current_root, file_size])
        return imageList

    def make_layout(self):

        left_col = [
            [sg.Text('Folder'), sg.In(size=(25, 1), enable_events=True, key='-FOLDER-'), sg.FolderBrowse()],
            # [sg.Listbox(values=[], enable_events=True, size=(40,20),key='-FILE LIST-')],
            [sg.Text('Convert:'),
             sg.Radio('None', "convertmode", default=True, size=(10, 1), key='-CONVERTNONE-', enable_events=True),
             sg.Radio('Convert to webp', "convertmode", size=(10, 1), key='-CONVERTWEBP-', enable_events=True),
             sg.Radio('Convert to jpg', "convertmode", size=(10, 1), key='-CONVERTJPG-', enable_events=True)],
            [sg.Text('Size (kb):'), sg.Text('Min'), sg.In(key='-MINSIZE-', default_text='0', size=(5, 1)),
             sg.Text('Max'), sg.In(default_text='5000', key='-MAXSIZE-', size=(5, 1)),
             sg.Button('Filter')],
            [sg.Text('Quality:'),
             sg.Slider(range=(1, 100), key='-CQUALITY-', orientation='h', size=(34, 20), default_value=85,
                       enable_events=True)],
            [sg.Text('PNG compress mode'),
             sg.Radio('P (8-bit pixels)', "pngmode", default=True, key='-PNGEIGHT-', size=(10, 1), enable_events=True),
             sg.Radio('RGB (3x8-bit)', "pngmode", key='-PNGRGB-', enable_events=True)],
            [sg.Button('GO!', key='-COMPRESS-')]
        ]

        tab1 = [[sg.Text('All images'), sg.Text('0', background_color='#28a745', key='-ALLIMAGES-')],
                [sg.Text('Images for compression'), sg.Text('0', background_color='#28a745', key='-COMIMAGES-')],
                [sg.Text('Progress'), sg.Text('0', background_color='#28a745', key='-DONE_PROGRESS-')],
                [sg.Text('Images skipped'), sg.Text('0', background_color='#28a745', key='-IMAGESSKIPPED-')],
                [sg.Text('Files compressed:'), sg.Text('0', background_color='#28a745', key='-FILESCOMPRESSED-')],
                [sg.Text('Saved:'), sg.Text('   ', background_color='#28a745', key='-MEMORYSAVED-')]]
        tab2 = [[sg.Output(size=(100,20))]]  # [sg.Output(size=(100,20))]

        right_col = [
            [sg.TabGroup([[sg.Tab('INFO', tab1, tooltip='tip'), sg.Tab('OUTPUT', tab2)]], tooltip='TIP2')]

        ]

        # ----- Full layout -----
        layout = [
            [sg.Column(left_col, element_justification='l'), sg.VSeperator(),
             sg.Column(right_col, element_justification='c')]
        ]

        # --------------------------------- Create Window ---------------------------------
        self.__window = sg.Window('Compresser', layout, resizable=False)

    def run_comp(self):
        self.counter = 0
        result: dict

        func = self.progress_update
        self.progress = True
        compress = ImagesCompress(self.folder,
                                  self.images_list,
                                  self.compress_quality,
                                  self.compress_mode,
                                  self.convert_mode)

        result = compress.compress_files(func)

        self.__window['-IMAGESSKIPPED-'].update(result['files_counter'] - result['compress_counter'])
        self.__window['-FILESCOMPRESSED-'].update(result['compress_counter'])
        self.__window['-MEMORYSAVED-'].update(
            f'{result["weight_before"]} -> {result["weight_after"]} : {int(result["weight_before"]) - int(result["weight_after"])} kb')



    def progress_update(self):

        val = int(self.__window['-DONE_PROGRESS-'].get())
        val += 1
        self.__window['-DONE_PROGRESS-'].update(val)

    def show_window(self):
        self.make_layout()

        window = self.__window

        while True:
            event, values = window.read()
            if event in (sg.WIN_CLOSED, 'Exit'):
                break
            elif event == sg.WIN_CLOSED or event == 'Exit':
                break
            elif event and self.progress is False:
                if event == 'Filter':
                    try:
                        self.min_size = int(values['-MINSIZE-'])
                        self.max_size = int(values['-MAXSIZE-'])
                        if self.folder and self.max_size > self.min_size:
                            self.images_list = []

                            self.images_list = self.listImages(self.folder, self.min_size, self.max_size)

                            window['-COMIMAGES-'].update(str(len(self.images_list)))
                        else:
                            sg.popup('Inorrect folder or min or max file size')
                    except:
                        print('Somethin wrong with filtering')

                elif event == '-CQUALITY-':
                    self.compress_quality = int(values['-CQUALITY-'])

                elif event == '-CONVERTNONE-':
                    self.convert_mode = 0
                elif event == '-CONVERTJPG-':
                    self.convert_mode = 1
                elif event == '-CONVERTWEBP-':
                    self.convert_mode = 2
                elif event == '-PNGEIGHT-':
                    self.compress_mode = 0
                elif event == '-PNGRGB-':
                    self.compress_mode = 1
                elif event == '-FOLDER-':  # Folder name was filled in, make a list of files in the folder
                    self.folder = values['-FOLDER-']
                    try:
                        file_list = self.listImages(self.folder)
                    except:
                        file_list = []

                    window['-ALLIMAGES-'].update(len(file_list))
                    window['-COMIMAGES-'].update(len(file_list))
                elif event == '-COMPRESS-':

                    if len(self.images_list):

                        # self.progress_el = int(values['-DONEPROGRESS-'])
                        threading.Thread(target=self.run_comp, daemon=True).start()
                    #
                        window['-COMPRESS-'].Update(visible=False)
                    else:
                        sg.popup('Click filter first!')

        window.close()


gui = GUI()
gui.show_window()
