from PIL import Image
import PIL
import os
import glob 
import re

#print(dir(Image))
def compress(image_quality : int, minSize, maxSize):

    errors = 'Errors:\n'

    frstregex = re.compile('(.*jpg$)|(.*jpeg$)|(.*gif$)|(.*png$)', re.IGNORECASE)
    

    location = os.walk("./")
    folder = 'compressed'
    
    if os.path.exists(folder):
        print("Dir exist")
        return


    for root, dirs, files in location: 
        for file in files:
            frstRes = re.match(frstregex, file)

            currentRoot = root.replace('\\','/')

            newRootList = currentRoot.split('/')
            newRootList.insert(1,folder)
            #print(newRootList)
            newRoot = '/'.join(newRootList)
            #print(newRoot)     

            if os.path.exists(newRoot) != True:
                os.makedirs(newRoot)
            if frstRes:
                fileSize = round(os.stat(currentRoot + "/" + file).st_size / 1024, 3)
                #print(fileSize)
                #print(file)
                if fileSize <= maxSize and fileSize >= minSize:
                    picture = Image.open('{}/{}'.format(root, file))
                    secRegex = re.compile('(jpg$)|(jpeg$)|(gif$)|(png$)|((.*)$)', re.IGNORECASE)
                    secRes = re.match(secRegex, picture.format)

                    #print(picture.format)
                    fileNameArr = file.split('.')
                    newFileName : str
                    imFormat : str

                    if secRes.group(1):
                        #print("jpg",file)
                        imFormat = fileNameArr[- 1]
                    if secRes.group(2):
                        #print("jpeg",file)
                        imFormat = fileNameArr[- 1]
                    if secRes.group(3):
                        # print("gif",file)
                        imFormat = fileNameArr[- 1]
                    if secRes.group(4):
                        #print("png",file)
                        try:
                            imFormat = picture.format
                            picture = picture.convert(
                            mode='P', # use mode='PA' for transparency
                            palette=Image.ADAPTIVE
                            )
                            picture.format = imFormat
                        except Exception as exc:
                            print(picture.format)
                            print(file)
                            print(type(exc))    # the exception instance
                            print(exc.args)     # arguments stored in .args
                            print(exc)          # __str__ allows args to be printed directly, # but may be overridden in exception subclasses
                    if secRes.group(5):
                        # print("other format",file)
                        imFormat = fileNameArr[- 1]


                    
                        #finally:
                        #    print('blabla') 
                    #else:
                        

                    #print('nazwa ' + str(fileNameArr[:-1]))
                    try:

                        newFileName = '{}/{}.{}'.format(newRoot,'.'.join(fileNameArr[:-1]), imFormat )
                        
                        picture.save(newFileName, optimize=True, quality=image_quality)

                        newFileSize = round(os.stat(newFileName).st_size / 1024, 3)
                        print("%s:   %f -> %f " %(file,fileSize,newFileSize))
                        #print(f'{file}:     {fileSize} -> {newFileSize}')
                        #picture.save("Compressed_"+file,optimize=True,quality=75)
                    except OSError:
                        
                        errors += f'{file}: Retarded file extension added by retarderd person... or something else happened \n\n'
                    except Exception as exc:
                        print(type(exc))
                        print(exc.args) 
                        print(exc)      
                        errors += f'{file}: {type(exc)} - {exc.args} - {exc}'
                    #finally:
                        #print('blabla')                              

                    #dim = picture.size

                    imFormat = fileNameArr[- 1]
                    if(imFormat != picture.format):
                        #print(newFileName)
                        #print(newRoot)
                        os.rename(newFileName, newRoot + "/" + str(file))
    print(errors)
           


print('Enter compress quality 0-100:')

quality : int = input()
quality = int(quality)


print('Enter min file size in kb: ')
imageMinSize = input()
imageMinSize = float(imageMinSize) 

print('Enter min file size in kb: ')
imageMaxSize = input()
imageMaxSize = float(imageMaxSize) 

if(quality >= 0 and quality <= 100 and imageMinSize < imageMaxSize and imageMinSize >= 0):
    compress(quality, imageMinSize, imageMaxSize)
else:
    print('fuk')


os.system('pause')

