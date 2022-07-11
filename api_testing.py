import cv2
import numpy as np
import requests
import io
import json


def is_alive():
    url_api = "http://127.0.0.1:8000/"
    result = requests.get(url_api)
    res = json.loads(result.content)

    print(res)


def langs_list():
    url_api = "http://127.0.0.1:8000/languages_list"
    result = requests.get(url_api)
    res = json.loads(result.content)

    print(res)


def translation_text_reg():
    img = cv2.imread("bigsleep.jpg")
    url_api = "http://127.0.0.1:8000/translation_text"

    _, compressedimage = cv2.imencode(".jpg", img, [1, 90])
    file_bytes = io.BytesIO(compressedimage)
    result = requests.post(url_api, data={"target_language": "pl"}, files={"img": file_bytes})
    res = json.loads(result.content)

    target_lan = res['target_language']
    original_text = res['original_text']
    translated_text = res['translated_text']

    print(target_lan)
    print()
    print(original_text)
    print()
    print(translated_text)


def translation_image_req():
    img = cv2.imread("bigsleep.jpg")
    url_api = "http://127.0.0.1:8000/translation_image"

    _, compressedimage = cv2.imencode(".jpg", img, [1, 90])
    file_bytes = io.BytesIO(compressedimage)

    result = requests.post(url_api, data={"target_language": "pl"}, files={"img": file_bytes})
    img_str = result.content
    nparr = np.frombuffer(img_str, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    cv2.imshow("res", img_np)
    cv2.waitKey(0)


if __name__ == '__main__':
    # is_alive()
    # langs_list()
    # translation_text_reg()
    translation_image_req()
