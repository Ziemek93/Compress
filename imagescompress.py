from xmlrpc.client import boolean
from PIL import Image
import os
import re
import sys

class ImagesCompress:
    FOLDER = 'Compressed'
    files_extensions = re.compile('(.*jpg$)|(.*jpeg$)|(.*gif$)|(.*png$)|(.*webp$)', re.IGNORECASE)
    error_string = ''
    counter = 0

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

    def get_file_format(self, file):
        fileNameArr = file.split('.')
        return fileNameArr[- 1]
    def get_file_name(self, file):
        fileNameArr = file.split('.')
        return fileNameArr[:- 1]
        
    def format_fix(self, name_format, file_format, path, new_name, file_name):
        if(name_format != file_format):                        
            os.rename(new_name, path + "/" + file_name)
            
    def ini_compress(self):
        if os.path.exists(self.FOLDER):
            print("Dir exist")
        else:
            self.make_them_light()
            print('\nFiles compressed: ' + str(self.counter))
            if(self.error_string):
                print('\nErrors: \n' + self.error_string)

    def compress_png(self, f_name, picture : Image):
        try:
            picture = picture.convert(
            mode='P', # use mode='PA' for transparency
            palette=Image.ADAPTIVE
            )
            return picture
        except Exception as exc:
            #print("%s -  %s: %s" %(picture.format,file,exc)) 
            self.error_string += f'PNG convert error: ({picture.format}) {f_name} - {type(exc)} - {exc}\n'
            
    def make_them_light(self):

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
                            
                            images_format_reg = re.compile('(jpg$)|(jpeg$)|(gif$)|(webp$)|(png$)|((.*)$)', re.IGNORECASE)
                            sec_regex_res = re.match(images_format_reg, picture.format)


                            if(convert == True): 
                                image_format = final_format
                                picture = picture.convert('RGB')
                            else:
                                file_format = self.get_file_format(file)
                                if sec_regex_res.group(5):
                                    #print("png",file)

                                    #Fix when image has the wrong format in the name
                                    image_format = picture.format
                                    picture = self.compress_png(file, picture)
                                elif(sec_regex_res):
                                    image_format = file_format
                        except Exception as exc:
                        #print("%s -  %s: %s" %(picture.format,file,exc)) 
                             

                            self.error_string += f'Image open: {file} (Line {sys.exc_info()[-1].tb_lineno}) - {exc}\n'

                                
                        
                            #finally:
                            #    print('blabla') 
                        #else:
                            
                        is_bigger_now = True
                        #print('nazwa ' + str(fileNameArr[:-1]))
                        try:
                        
                            new_file_name = '{}/{}.{}'.format(paths['new'],'.'.join(self.get_file_name(file)), image_format )
                            
                            
                            
                            picture.save(new_file_name, optimize=True, quality=self.image_quality)
    
                            new_file_size = round(os.stat(new_file_name).st_size / 1024, 3)
                            is_bigger_now = bool(file_size < new_file_size) 
                            print("%s (%s):   %f -> %f " %(file,image_format,file_size,new_file_size))

                            self.counter += 1
                            if(is_bigger_now == True):
                                os.remove(new_file_name)
                                print("File is bigger now - aborted")
                                self.counter -= 1
                            elif(convert == False):
                            #print(f'{file}:     {fileSize} -> {new_file_size}')
                            #picture.save("Compressed_"+file,optimize=True,quality=75) 
                                self.format_fix(file_format, picture.format, paths['new'], new_file_name,  str(file))
                                
                            

                        except Exception as exc:
                            self.error_string += f'Save error: ({picture.format}) {file}({image_format}) (Line {sys.exc_info()[-1].tb_lineno}) - {exc}\n'
                        #finally:
                            #print('blabla')                              
    
                        #dim = picture.size
    
                        
    
    

    
    