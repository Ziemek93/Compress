
import os
from imagescompress import ImagesCompress

print('Enter compress quality 0-100:')

quality : int = input()
quality = int(quality)
decision = ''
change_format = 0

print('Enter min file size in kb: ')
imageMinSize = input()
imageMinSize = float(imageMinSize) 

print('Enter max file size in kb: ')
imageMaxSize = input()
imageMaxSize = float(imageMaxSize) 

print('Convert to webp? (y/n)')
decision = input()
if(str(decision) != 'y'):
    print('Convert to jpg? (y/n)')
    decision = input()
    if(str(decision) == 'y'):
        change_format = 1
else:
    change_format = 2         

if(quality >= 0 and quality <= 100 and imageMinSize < imageMaxSize and imageMinSize >= 0):
    komp = ImagesCompress(imageMinSize, imageMaxSize, quality, change_format)
    komp.compress_files()
    #compress(quality, imageMinSize, imageMaxSize)
else:
    print('fuk')


os.system('pause')