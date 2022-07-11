import fastapi
from fastapi.responses import Response
import uvicorn
import numpy as np
import cv2
import io

from schemas import TextTranslation
from services import get_translated_image, get_translated_text

app = fastapi.FastAPI(debug=True)

languages = ('en', 'de', 'fr', 'hi', 'pl', 'sp')


@app.get("/")
def is_alive():
    return {"status": "alive"}


@app.get("/languages_list")
def languages_list():
    return {"Languages": languages}


@app.post("/translation_image")
async def translation_image(target_language: str = fastapi.Form(...), img: fastapi.UploadFile = fastapi.File(...)):
    target_language = target_language.lower()
    if target_language in languages:
        try:
            content = await img.read()
            nparr = np.frombuffer(content, np.uint8)
            file = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            translated_img = get_translated_image(img=file, dest_lang=target_language)

            res, im_png = cv2.imencode(".png", translated_img)
            to_bytes_img = io.BytesIO(im_png.tobytes())

            return Response(content=to_bytes_img.getvalue(), headers={"target_lang": target_language}, media_type="image/png")
        except IndexError:
            raise fastapi.HTTPException(status_code=500, detail=f"Something went wrong")

    else:
        raise fastapi.HTTPException(status_code=400, detail=f"There is no such language like: {target_language}. "
                                                            f"Here's list of available languages: {languages}")


@app.post("/translation_text", response_model=TextTranslation)
async def translation_text(target_language: str = fastapi.Form(...), img: fastapi.UploadFile = fastapi.File(...)):
    target_language = target_language.lower()
    if target_language in languages:
        try:
            content = await img.read()
            nparr = np.frombuffer(content, np.uint8)
            file = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            data = get_translated_text(dest_lang=target_language, img=file)

            return data
        except IndexError:
            raise fastapi.HTTPException(status_code=500, detail=f"Something went wrong")
    else:
        raise fastapi.HTTPException(status_code=400, detail=f"There is no such language like: {target_language}. "
                                                            f"Here's list of available languages: {languages}")


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
