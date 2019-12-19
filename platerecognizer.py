import os
import sys
import re
import time
import pickle
import argparse
import ftplib

import requests

from PIL import Image, ImageDraw, ImageFont
from pprint import pprint

from car_detect.detector import Car_Detector



#--------------------------------------------------------------------------------------------------

print(sys.argv)
# Parse args
server_url = sys.argv.pop(1)
if re.fullmatch('((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}', server_url) is not None:
    if server_url[len(server_url)-1] == '.':
        server_url = server_url[:-1]
else:
    print('Error in server address')
    exit(0)

port = sys.argv.pop(1)
user = sys.argv.pop(1)
server_dir = sys.argv.pop(1)


def get_plate_type(plate_str):
    """
    Return 1 if plate is new style, 0 if not, -1 if is a wrong plate
    """
    new_plate_regex = '([A-Za-z]{2}[0-9]{3}[A-Za-z]{2})'
    old_plate_regex = '([A-Za-z]{3}[0-9]{3})'

    if re.fullmatch(new_plate_regex, plate_str) is not None:
        return 1

    if re.fullmatch(new_plate_regex, plate_str) is not None:
        return 0

    return -1


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=
        'Read license plates from images and output the result as JSON.',
        epilog=
        'For example: python plate_recognition.py ftp-server --port --creds --server-dir --output-folder'
    )
    parser.add_argument('-port', '-p', '--port', help='Port of ftp-server.', required=False)
    parser.add_argument('-dir', '-d', '--server-dir', help='Directory path in server where images are allocated', required=True)
    parser.add_argument('-out', '-o', '--output-folder',help="Directory to save image with plate", required=False)
    parser.add_argument('-user', '-u', '--user',help="Authentication for ftp in format user:pass", required=False)
    return parser.parse_args()


#args = parse_arguments()

# check ouput folder
#if args.out:
#    plates_dir = args.out

def check_dirs(dirs):
    for d in dirs:
        try:
            os.mkdir(dirs)
        except:
            print('Couldn\'t create {} folder'.format(d))


#if not os.path.exists(plates_dir):
#    os.mkdir(plates_dir) 

#if not os.path.exists(tmp_dir):
#    os.mkdir(tmp_dir)
#--------------------------------------------------------------------------------------------------


# FTP function
def connect_ftp(addr, port='9999', dir_='.'):
    global user
    ftp = ftplib.FTP()
    try:
        ftp.connect(addr, int(port))
    except Exception as ex:
        print('Couldn\'t connect to {}:{} ftp-server.\nPlease check address'.format(addr, port))

    if user:
        user, password = user.split(':')
        try:
            ftp.login(user, password)
        except Exception as ex:
            print('Couldn\'t login with {} user.\nPlease check user and password'.format(user))
            exit(0)
    else:
        ftp.login()
        print('connected with anonymous user')

    try:
        ftp.cwd(dir_)
    except Exception as ex:
        print('Couldn\'t find {} dir.\nYou do not have permissions or the directory does not exist'.format(dir_))
        exit(0)
    return ftp


ftp = connect_ftp(server_url, port, server_dir)
#--------------------------------------------------------------------------------------------------


# Call to API-PlateRecognizer
def plate_recognizer(image_path, api_call=True):
    if not api_call:
        with open('new_response.pickle', 'rb') as fp:
            response = pickle.load(fp)
        return response
    else:
        with open(image_path, 'rb') as fp:
            response = requests.post(
                API_URL,
                files=dict(upload=fp),
                headers={'Authorization': 'Token {}'.format(API_TOKEN)}
                )
    return response.json()
#pprint(response.json())
#--------------------------------------------------------------------------------------------------


def get_probably_char(candidates, index, func):
    for candidate in candidates:
        n_plate = candidate['plate']
        if getattr(n_plate[index], func)(): 
            return n_plate[index]


    
connect_tried = 0
while True:
    try:
        files = ftp.nlst()
        if not files:
            print("no new images")
            time.sleep(10)
            continue
    except Exception as ex:
        ftp = connect_ftp(server_url, port, dir_)
        connect_tried += 1
        if connect_tried > 10:
            print('No se puede conectar al server')
            break
        continue

    connect_tried = 0

    for file in files:
        print('Getting {} file from ftp-server'.format(file))
        with open(os.path.join(tmp_dir, file), 'wb') as fp:
            print(ftp.retrbinary('RETR {}'.format(file), fp.write, blocksize=1024*1024*1024))

        response = plate_recognizer(os.path.join(tmp_dir, file))
        #        if 'status_code' in response:

        #with open('new_response.pickle', 'wb') as fp:
        #    pickle.dump(response, fp)
        # Parse api response
        result = response['results']
        result = result[0] if isinstance(result, list) else result 

        plate_box = list(result['box'].values())  # ymin, xmin, ymax, xmax 
        plate_box = [plate_box[1]-10, plate_box[0]-10, plate_box[3]+10, plate_box[2]+10]
        plate = result['plate']

        is_new_plate = 1 if len(plate) == 7 else 0
        print('\nplate: ', plate, 'is_new: ', bool(is_new_plate))
        
        for i in range(len(plate)):
            if (is_new_plate and (i in [0,1,5,6])) or ((not is_new_plate) and (i in [3,4,5])):
                if not plate[i].isnumeric():
                    c = get_probably_char(result['candidates'], i, 'isnumeric')
                    l = list(plate)
                    l[i] = c
                    plate = ''.join(l)
            else:
                if not plate[i].isalpha():
                    c = get_probably_char(result['candidates'], i, 'isalpha')
                    l = list(plate)
                    l[i] = c
                    plate = ''.join(l)
        plate = plate.upper()
#--------------------------------------------------------------------------------------------------

        # Save plates
        img = Image.open(os.path.join(tmp_dir, file))
        #draw = ImageDraw.Draw(img)
        #font = ImageFont.truetype("arial.ttf", 15)

        #draw.rectangle(plate_box, outline='red')
        #draw.text((plate_box[0], plate_box[1]), plate, fill='red')
        #img.save(os.path.join(plates_dir, plate+'_draw.jpg'))
        img = img.crop(tuple(plate_box))
        img.save(os.path.join(plates_dir, plate+'.jpg'))
        print('New plate image saved in {}'.format(plates_dir))
    break