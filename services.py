import os
from random import choice
from string import ascii_uppercase
import unidecode
from googletrans import Translator
from pytesseract import Output
import pytesseract
import cv2
import numpy as np
import requests
import io

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def process_data(left_coords: list, right_coords: list, sents):
    left_coords = list(filter(None, left_coords))
    right_coords = list(filter(None, right_coords))
    # print(translated_sent)
    sents = sents.split("\n")
    sents = [sent for sent in sents if sent != ""]

    return left_coords, right_coords, sents


def get_optimal_font_scale(text, x1, x2):
    width = x2 - x1
    for scale in reversed(range(0, 60, 1)):
        textSize = cv2.getTextSize(text, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=scale/10, thickness=1)
        new_width = textSize[0][0]
        if new_width <= width:
            return (scale/10) + .5
    return 1


def get_text_center(text, x1, y1, x2, y2, size, t) -> list:
    # get boundary of this text
    textsize = cv2.getTextSize(text, cv2.FONT_HERSHEY_PLAIN, size, t)[0]

    w = x2 - x1
    h = y2 - y1

    textX = x1 + w // 2
    textY = y1 + h // 2

    return [textX, textY, textsize]


def get_translated_image(*, dest_lang="pl", img):
    translator = Translator()

    img = cv2.resize(img, (1280, 720))
    img_org = img.copy()
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    adaptive_threshold = cv2.adaptiveThreshold(gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 85, 11)
    d = pytesseract.image_to_data(adaptive_threshold, output_type=Output.DICT)
    n_boxes = len(d['level'])

    statement = ""
    last_word = ""

    left_coords_list = []
    right_coords_list = []
    left_coords = []
    right_coords = []

    for i in range(n_boxes):
        # translated = translator.translate(text=d['text'][i], dest="pl", src="en")
        if d['text'][i] != '' and d['text'][i] != ' ':
            statement += f"{d['text'][i]} "

            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            cv2.rectangle(img_org, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # cx, cy = int(x + w // 2), int(y + h // 2)

            # kordy lewe i prawe
            left_coords.append((x, y))
            right_coords.append((x + w, y + h))
        else:
            if last_word != '' and d['text'][i] != ' ':
                statement += f"\n"
                # jak jest enter to dodac dog glownych ldist, bo chce brac punkty zdan
                left_coords_list.append(left_coords)
                right_coords_list.append(right_coords)
                left_coords = []
                right_coords = []

        last_word = d['text'][i]

    translated_sent = translator.translate(text=statement, dest=dest_lang).text
    translated_sent = unidecode.unidecode(translated_sent)

    left_coords_list, right_coords_list, sents = process_data(left_coords_list, right_coords_list, translated_sent)

    for i in range(len(right_coords_list)):
        left_coords_chunk = np.array(left_coords_list[i])
        right_coords_chunk = np.array(right_coords_list[i])
        sent = sents[i]

        left_x = np.min(left_coords_chunk[:, 0])
        left_y = np.min(left_coords_chunk[:, 1])

        right_x = np.max(right_coords_chunk[:, 0])
        right_y = np.max(right_coords_chunk[:, 1])

        cv2.rectangle(img, (left_x, left_y), (right_x, right_y), (255, 255, 255), -1)

        font_size = get_optimal_font_scale(sent, left_x, right_x)
        text_x, text_y, text_size = get_text_center(sent, left_x, left_y, right_x, right_y, font_size, 2)

        cv2.putText(img, f"{sent}", (text_x - text_size[0] // 2, text_y + text_size[1] // 2), cv2.FONT_HERSHEY_PLAIN, font_size,
                    (0, 0, 0), 2)

    return img


def get_translated_text(*, dest_lang="pl", img):
    translator = Translator()

    img = cv2.resize(img, (1280, 720))

    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    adaptive_threshold = cv2.adaptiveThreshold(gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 85, 11)
    d = pytesseract.image_to_data(adaptive_threshold, output_type=Output.DICT)
    n_boxes = len(d['level'])

    statement = ""
    last_word = ""
    for i in range(n_boxes):
        if d['text'][i] != '' and d['text'][i] != ' ':
            statement += f"{d['text'][i]} "
        else:
            if last_word != '' and d['text'][i] != ' ':
                statement += f"\n"

        last_word = d['text'][i]

    translated_sent = translator.translate(text=statement, dest=dest_lang).text
    translated_sent = unidecode.unidecode(translated_sent)

    return {"target_language": dest_lang, "original_text": statement, "translated_text": translated_sent}


if __name__ == '__main__':
    img = cv2.imread("bigsleep.jpg")
    data = get_translated_text(img=img)
    print(data)

