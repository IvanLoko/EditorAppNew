import cv2
import numpy as np
import matplotlib.pyplot as plt
import math

from recognize import recognize
from ultralytics import YOLO
#from ultralytics.yolo.utils.plotting import Annotator

import json
import base64
import pickle
import PIL.Image
from io import BytesIO
import os
import glob
import pathlib
from normalizer import splitter

input_files = './cb/forbidden/*'
output_dir = "./cropped_imgs_new"

plt.rcParams['figure.figsize'] = [15, 10]

model = YOLO("./segmentator.pt")

def im2base64(img):
    """Convert a Numpy array to JSON string"""
    # You may need to convert the color.
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    im_pil = PIL.Image.fromarray(img)

    buffered = BytesIO()
    im_pil.save(buffered, format="JPEG")
    # img_str = base64.b64encode(buffered.getvalue())

    #imdata = pickle.dumps(im)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def findPin(elem, th=10):
    h2 = elem.shape[0] // 2
    w2 = elem.shape[1] // 2

    maxN = -1
    possiblePin = (0, 0)
    for pin, part in [
            ((0, 0), elem[:h2, :w2]),
            ((0, 1), elem[:h2, w2:]),
            ((1, 1), elem[h2:, w2:]),
            ((1, 0), elem[h2:, :w2])
        ]:
        n = np.sum(part > th)
        # print(n)
        if n > maxN:
            maxN = n
            possiblePin = pin

    return possiblePin

def getSegments(image, conf=0.55, **kwargs):
    results = model.predict(image, save=False,  conf=conf, **kwargs)
    
    rects = { }
    for name in model.names:
        name = model.names[name]
        rects[name] = []

    for r in results:
        boxes = r.boxes
        for box in boxes:
            b = box.xyxy[0]  # get box coordinates
            c = box.cls      # TODO: класс сегмента

            name = model.names[int(c)]
            rects[name].append(b)
    return rects

def normalizeWord(word):
    start_word = word[:1]
    last_word = word[1:]
    for old, new in [
        ('a', '0'),
        ('b', '6'),
        ('c', '6'),
        ('d', '8'),
        ('e', '8'),
        ('f', '9'),
        ('g', '9'),
        ('h', '6'),
        ("i", "1"), 
        ("j", "1"), 
        ("k", "1"),
        ("l", "1"),
        ("m", "0"), 
        ("n", "0"), 
        ("o", "0"),
        ("p", "8"),
        ("q", "9"),
        ("r", "6"),
        ('s', '5'),
        ('t', '4'),
        ('u', '4'),
        ('v', '0'),
        ('w', '0'),
        ('x', '4'),
        ('y', '4'),
        ('z', '2'),
        ]:
        last_word = last_word.replace(old, new)
    if len(start_word) > 0:
        if start_word == '0':
            word = "D" + last_word
        elif start_word in "123456789":
            word = "D" + last_word
        else:
            word = start_word + last_word
    else:
        word = start_word + last_word
    return word

def preparate(filename, margin = 5):
    # f"./cb/{file}.jpg"
    file = pathlib.Path(filename).stem
    if len(glob.glob(f"{output_dir}/{file}*.json")) > 0:
        return

    #image = cv2.imread(filename)
    for number, cropped_image in enumerate(splitter(filename)):
        img = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
        canvas = cropped_image.copy()

        _, cropped_tresh = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU)
        cropped_tresh = cv2.bitwise_not(cropped_tresh)

        rects = getSegments(cropped_image)

        chips_info = []
        for i, rect in enumerate(rects["micro"]):
            # пытаемся понять что внутри контура
            x, y, x2, y2 = list(map(int, rect))
            w, h = x2-x, y2-y

            elem = cropped_image[y:y2, x:x2]
            
            # xm, ym, wm, hm = x - margin, y - margin, w + 2 * margin, h + 2 * margin
            elem_bin = cropped_tresh[y-margin:y2+margin, x-margin:x2+margin]

            wordsRecognized = recognize(elem, confThreshold=0.8, nmsThreshold=0.4)
            info = None

            ht, wt = cropped_tresh.shape
            word = ""
            if len(wordsRecognized) > 0:
                info = wordsRecognized[0]
                
                word = normalizeWord(info["word"])
                print(info["word"], "->", word)

                (x1, y1), (x2, y2) = info["rect"]
                word_rect = info["rect"]

                cx, cy = info["p"][0]
                cv2.putText(canvas, word, (int(x + cx),int(y + cy - (y2-y1) / 2)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), thickness=1)

                # print((x1, y1), (x2, y2), x, y, x+w, y+h)
                cropped_tresh[y+y1:min(y+y2, ht), x+x1:min(x+x2, wt)] = np.zeros_like(cropped_tresh[y+y1:min(y+y2, ht), x+x1:min(x+x2, wt)])

            # удалить возможные шумы
            kernel = np.ones((5,5),np.uint8)
            opening = cv2.morphologyEx(elem_bin, cv2.MORPH_OPEN, kernel)

            ix, iy = findPin(opening)
            cx, cy = ix * w / 2 + w / 4, iy * h / 2 + h / 4
            chips_info.append({
                "label": "micro-" + word,
                "points": [ [x, y], [x+w, y+h] ],
                "group_id": i,
                "description": "micro",
                "shape_type": "rectangle",
                "flags": {}
            })
            r = min(w, h) / 32
            chips_info.append({
                "label": "pin-" + word,
                "points": [ [x + cx, y + cy], [x + cx + r, y + cy + r] ],
                "group_id": i,
                "description": "pin of micro",
                "shape_type": "circle",
                "flags": {}
            })
    
        cv2.imwrite(f"{output_dir}/{file}-{number}.jpg", cropped_image)
        h, w, _ = cropped_image.shape
        json_val = {
            "version": "5.2.0.post4",
            "flags": {},
            "shapes": chips_info,
            "imagePath": f"{output_dir}/{file}.jpg",
            "imageData": im2base64(canvas),
            "imageHeight": h,
            "imageWidth": w
        }
        with open(f'{output_dir}/{file}-{number}.json', 'w') as fp:
            json.dump(json_val, fp)

if __name__ == "__main__":
    for file in glob.glob(input_files):
        if os.path.isfile(file):
            print(file)
            preparate(file)