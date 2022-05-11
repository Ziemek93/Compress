from PIL import Image
import os
import re
import sys
import codecs

class ImagesCompress:
    FOLDER = 'Compressed'
    files_before_comp = 0.0
    files_after_comp = 0.0
    percent_diff : int
    files_extensions = re.compile('(.*jpg$)|(.*jpeg$)|(.*gif$)|(.*png$)|(.*webp$)|(.*tiff)', re.IGNORECASE)
    log_file = ''
    error_string = ''
    counter = 0
    files_skipped = 0

    def __init__(self, minSize : int, maxSize : int, image_quality : int, change_format = 0):
        self.minSize = minSize
        self.maxSize = maxSize
        self.image_quality = image_quality
        self.change_format = change_format

    def get_path(self, root : str):
        current_root = root.replace('\\','/')
        new_root_list = current_root.split('/')
        new_root_list.insert(1,self.FOLDER)
        new_root = '/'.join(new_root_list)
        if os.path.exists(new_root) != True:
            os.makedirs(new_root)

        return {'current': current_root, 'new': new_root}

    # def get_file_format(self, file):
    #     fileNameArr = file.split('.')
    #     return fileNameArr[- 1]
    # def get_file_name(self, file):
    #     fileNameArr = file.split('.')
    #     return fileNameArr[:- 1]

    #Fix file format extension
    def format_fix(self, name_format, file_format, path, new_name, file_name):
        if(name_format != file_format):                        
            os.rename(new_name, path + "/" + file_name)
            
    def compress_files(self):
        if os.path.exists(self.FOLDER):
            print("Dir exist")
        else:
            self.make_them_light()

            if(self.files_before_comp > 0 and self.files_before_comp > 0):
                self.percent_diff = int((self.files_after_comp / self.files_before_comp) * 100)
                compress_info = f'Saved: {self.files_before_comp} -> {self.files_after_comp} : {self.files_before_comp - self.files_after_comp} ({100 - self.percent_diff})%'
                self.save_log(compress_info)
                print(compress_info)
                files_compressed = '\nFiles compressed: ' + str(self.counter)
                self.save_log(files_compressed)
                print(files_compressed)
            
            print('\nFiles not compressed: ' + str(self.files_skipped - self.counter))

            if(self.error_string):
                self.save_log('\nErrors: \n' + self.error_string)
                print('\nErrors: \n' + self.error_string)
            self.close_log_file()

    def format_png(self, f_name, picture : Image):
        try:
            picture = picture.convert(
            mode= 'P', # use mode='PA' for transparency
            palette=Image.ADAPTIVE, colors=256
            )


            #picture = picture.convert(
            #mode= 'RGBA', # use mode='PA' for transparency
            #palette=Image.ADAPTIVE, colors=256
            #)
            ##picture_rgb = picture.convert(mode='RGBA') # convert RGBA to RGB
            ##picture = picture.quantize(colors=256, method=Image.MAXCOVERAGE)
            return picture
        except Exception as exc:
            #print("%s -  %s: %s" %(picture.format,file,exc)) 
            self.error_string += f'PNG convert error: ({picture.format}) {f_name} - {type(exc)} - {exc}\n'


    def close_log_file(self):
        if(self.log_file != ''):
            self.log_file.close()
    def save_log(self, text : str):
        if(self.log_file == ''):
            self.log_file = codecs.open('compress_log.txt', 'w+', 'utf-8')
        self.log_file.write(text + "\n")
    def metadada(img :Image):
        data = list(img.getdata())
        image_without_exif = Image.new(img.mode, img.size)
        image_without_exif.putdata(data)
        return image_without_exif

    def make_them_light(self):
        clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

    
        Image.MAX_IMAGE_PIXELS = None

        final_format : str
        #format = 0
        convert = False
        match(self.change_format):
            case 0:
                final_format = ''
            case 1:
                final_format = 'jpg'
                convert = True
            case 2:
                final_format = 'webp'
                convert = True
        print(self.change_format)
        for root, dirs, files in os.walk("./"): 
            for file in files:
                clearConsole()
                frst_regex_res = re.match(self.files_extensions, file)
    
                paths = self.get_path(root)


                if frst_regex_res:
                    file_size = round(os.stat(paths['current'] + "/" + file).st_size / 1024, 3)
                    #print(file_size)
                    #print(file)
                    new_file_name : str
                    image_format : str
 
                    if file_size <= self.maxSize and file_size >= self.minSize:
                        try:
                            picture = Image.open('{}/{}'.format(root, file))
                            
                            images_format_reg = re.compile('(jpg$)|(jpeg$)|(gif$)|(webp$)|(png$)|(tiff$)|((.*)$)', re.IGNORECASE)
                            sec_regex_res = re.match(images_format_reg, picture.format)

                            if(convert == True): 
                                image_format = final_format
                                if(final_format == 'webp'):
                                    picture = picture.convert('RGBA')
                                else:
                                    picture = picture.convert('RGB')

                            else:
                                arr = file.split('.')
                                file_format = arr[- 1]
                                if sec_regex_res.group(5):
                                    #print("png",file)

                                    #Fix when image has the wrong format in the name
                                    image_format = picture.format
                                    picture = self.format_png(file, picture)
                                elif(sec_regex_res):
                                    image_format = file_format
                        except Exception as exc:
                             
                            self.error_string += f'Image open: {file} (Line {sys.exc_info()[-1].tb_lineno}) - {exc}\n'
                            picture = self.metadada(picture)
                                
                            
                        is_bigger_now = True
                        try:
                            arr = file.split('.')
                            new_file_name = '{}/{}.{}'.format(paths['new'],'.'.join(arr[:- 1]), image_format )
                            
                            
                            
                            picture.save(new_file_name, optimize=True, quality=self.image_quality)
    
                            new_file_size = round(os.stat(new_file_name).st_size / 1024, 3)
                            is_bigger_now = bool(int(file_size) < int(new_file_size)) 
                            info = "%s (%s):   %f -> %f " %(file,image_format,file_size,new_file_size)
                            print(info)

                            self.save_log(info)
                            self.files_skipped += 1

                            if(is_bigger_now == True):
                                os.remove(new_file_name)
                                self.save_log("File is bigger now - aborted")
                                print("File is bigger now - aborted")

                                continue
                            elif(convert == False):
                                self.format_fix(file_format, picture.format, paths['new'], new_file_name,  str(file))

                            self.counter += 1
                            self.files_before_comp += int(file_size)
                            self.files_after_comp +=  int(new_file_size)
                            

                        except Exception as exc:
                            self.error_string += f'Save error: ({picture.format}) {file}({image_format}) (Line {sys.exc_info()[-1].tb_lineno}) - {exc}\n'
                                   
        self.save_log(self.error_string)
    
                        
    
    

    
    