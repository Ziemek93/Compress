from array import array
from PIL import Image
import os
import re
import sys
import codecs


class ImagesCompress:
    FOLDER_NAME = 'Compressed'
    # files_before_comp = 0.0
    # files_after_comp = 0.0
    # counter = 0
    files_extensions = re.compile('(.*jpg$)|(.*jpeg$)|(.*gif$)|(.*png$)|(.*webp$)|(.*tiff)', re.IGNORECASE)
    log_file = ''
    error_string = ''

    def __init__(self, basic_folder: str, images_list: list, image_quality: int, png_mode=0, change_format=0):
        self.images_list = images_list
        self.image_quality = image_quality
        self.change_format = change_format
        self.png_mode = png_mode

        # temp = basic_folder.split('/')
        self.basic_folder = basic_folder
        self.basic_path_len = len(basic_folder.split('/'))

    def get_path(self, root: str):
        current_root = root.replace('\\', '/')
        new_root_list = current_root.split('/')
        new_root_list.insert(self.basic_path_len, self.FOLDER_NAME)
        new_root = '/'.join(new_root_list)

        number_of_unique_elements = current_root.count('Compressed')
        # if number_of_unique_elements > 1:
        #    print('uh')
        if not os.path.exists(new_root):
            os.makedirs(new_root)

        return {'current': current_root, 'new': new_root}

    # def get_file_format(self, file):
    #     fileNameArr = file.split('.')
    #     return fileNameArr[- 1]
    # def get_file_name(self, file):
    #     fileNameArr = file.split('.')
    #     return fileNameArr[:- 1]

    # Fix file format extension
    def format_fix(self, name_format, file_format, path, new_name, file_name):
        if name_format != file_format:
            os.rename(new_name, path + "/" + file_name)

    def compress_files(self, pointer):
        # if os.path.exists(self.FOLDER_NAME):
        #    print("Dir exist")
        # else:
        result: dict
        result = self.make_them_light(pointer)

        # result["counter"]
        # result["images_skipped"]
        # result["weight_before"]
        # result["weight_after"]

        if result['weight_before'] > 0 and result['weight_after'] > 0:
            percent_diff = int((result["weight_after"] / result["weight_before"]) * 100)
            compress_info = f'Saved: {result["weight_before"]} -> {result["weight_after"]} : {result["weight_before"] - result["weight_after"]} ({100 - percent_diff})% '
            self.save_log(compress_info)
            print(compress_info)
            files_compressed = '\nFiles compressed: ' + str(result['compress_counter'])
            self.save_log(files_compressed)
            print(files_compressed)

        print('\nFiles not compressed: ' + str(result['files_counter'] - result['compress_counter']))

        if self.error_string:
            self.save_log('\nErrors: \n' + self.error_string)
            print('\nErrors: \n' + self.error_string)
        self.close_log_file()
        print(self.error_string)

        return result

    def format_png(self, f_name, picture: Image):
        try:
            if self.png_mode == 0:
                picture = picture.convert(
                    mode='P',  # use mode='PA' for transparency
                    palette=Image.ADAPTIVE)
            else:

                picture = picture.convert(
                    mode='RGBA',
                    palette=Image.ADAPTIVE)

            # picture = picture.convert(
            # mode= 'RGBA', # use mode='PA' for transparency
            # palette=Image.ADAPTIVE, colors=256
            # )
            ##picture_rgb = picture.convert(mode='RGBA') # convert RGBA to RGB
            ##picture = picture.quantize(colors=256, method=Image.MAXCOVERAGE)
            return picture
        except Exception as exc:
            # print("%s -  %s: %s" %(picture.format,file,exc))
            self.error_string += f'PNG convert error: ({picture.format}) {f_name} - {type(exc)} - {exc}\n'

    def close_log_file(self):
        if self.log_file != '':
            self.log_file.close()

    def save_log(self, text: str):
        if self.log_file == '':
            self.log_file = codecs.open(self.basic_folder + '/compress_log.txt', 'w+', 'utf-8')

        self.log_file.write(text + "\n")

    #to repair, somtetimes make images black
    def remove_metadada(self, img: Image):
        data = list(img.getdata())
        image_without_exif = Image.new(img.mode, img.size)
        image_without_exif.putdata(data)
        return image_without_exif

    def make_them_light(self, pointer):
        # clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

        Image.MAX_IMAGE_PIXELS = None
        files_before_comp = 0.0
        files_after_comp = 0.0
        compress_counter = 0
        files_counter = 0

        # files_skipped = 0

        final_format = ''
        # format = 0
        convert = False
        match self.change_format:
            # case 0:
            #    final_format = ''
            case 1:
                final_format = 'jpg'
                convert = True
            case 2:

                final_format = 'webp'
                convert = True

        # print(self.change_format)

        for file, file_path, file_size in self.images_list:
            # pointer += 1
            # clearConsole()
            frst_regex_res = re.match(self.files_extensions, file)

            paths = self.get_path(file_path)
            new_file_name: str
            image_format: str

            try:
                picture = Image.open('{}/{}'.format(file_path, file))

                images_format_reg = re.compile('(jpg$)|(jpeg$)|(gif$)|(webp$)|(png$)|(tiff$)|((.*)$)', re.IGNORECASE)
                sec_regex_res = re.match(images_format_reg, picture.format)
                if convert:
                    image_format = final_format
                    if final_format == 'webp':
                        picture = picture.convert('RGBA')
                    else:
                        picture = picture.convert('RGB')
                else:
                    arr = file.split('.')
                    file_format = arr[- 1]
                    if sec_regex_res.group(5):
                        # print("png",file)
                        # Fix when image has the wrong format in the name
                        image_format = picture.format
                        picture = self.format_png(file, picture)
                    elif sec_regex_res:
                        image_format = file_format
                    else:
                        raise Exception("File format issue - skipped")
            except Exception as exc:

                self.error_string += f'Image open: {file} (Line {sys.exc_info()[-1].tb_lineno}) - {exc}\n'
                continue

            #picture = self.remove_metadada(picture)
            is_bigger_now = True
            try:
                arr = file.split('.')
                new_file_name = '{}/{}.{}'.format(paths['new'], '.'.join(arr[:- 1]), image_format)

                picture.save(new_file_name, optimize=True, quality=self.image_quality)
                new_file_size = round(os.stat(new_file_name).st_size / 1024, 3)
                is_bigger_now = bool(int(file_size) < int(new_file_size))
                info = "%s (%s):   %f -> %f " % (file, image_format, file_size, new_file_size)
                # print(info)
                self.save_log(info)
                files_counter += 1

                pointer()
                if is_bigger_now:
                    os.remove(new_file_name)
                    self.save_log(f"{file} file is bigger now - aborted")
                    # print(f"{file} file is bigger now - aborted")
                    continue
                elif not convert:
                    self.format_fix(file_format, picture.format, paths['new'], new_file_name, str(file))
                compress_counter += 1
                files_before_comp += int(file_size)
                files_after_comp += int(new_file_size)

            except Exception as exc:
                self.error_string += f'Save error: ({picture.format}) {file}({image_format}) (Line {sys.exc_info()[-1].tb_lineno}) - {exc}\n'

        return {'compress_counter': compress_counter, 'files_counter': files_counter,
                'weight_before': files_before_comp,
                'weight_after': files_after_comp}
        self.save_log(self.error_string)
