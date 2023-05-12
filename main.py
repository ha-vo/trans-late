from flask import Flask, render_template, request, make_response
import pytesseract
from googletrans import Translator
import googletrans
import os
from PIL import Image
from gtts import gTTS
from os.path import exists
from langdetect import detect
from PyPDF2 import PdfReader

secrect_key = os.urandom(32)

UPLOAD_FOLDER = 'upload'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__, static_folder='public')
app.secret_key = secrect_key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'
config = '--tessdata-dir "C:/Program Files (x86)/Tesseract-OCR/tessdata"'
translator = Translator()


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def home():
    contentSrc = ''
    contentDest = ''
    src = ''
    dest = ''
    if request.method == 'POST':
        src = str(request.form['src'])
        dest = str(request.form['dest'])
        content = str(request.form['content'])
        if src == '' and content != '':
            src = detect(content)

        if content:
            contentSrc = content
            contentDest = translator.translate(
                content, src=src, dest=dest).text
        if request.files['file']:
            img = Image.open(request.files['file'])
            test = pytesseract.image_to_string(img, config=config)
            test = test.strip()
            contentSrc = test
            if src == '':
                src = detect(contentSrc)
            contentDest = translator.translate(
                test, src=src, dest=dest).text
        if request.files['filepdf']:
            reader = PdfReader(request.files['filepdf'])
            page = reader.pages[0]
            s = page.extract_text()
            s = s.replace(' ', '')
            contentSrc = s
            if src == '':
                src = detect(contentSrc)
            contentDest = translator.translate(
                s, src=src, dest=dest).text
        if exists('public/voice.mp3'):
            os.remove('public/voice.mp3')
        tts = gTTS(contentSrc, lang=src)
        tts.save('public/voice.mp3')
    languages = googletrans.LANGUAGES
    return render_template('interface.html', languages=languages, contentSrc=contentSrc, contentDest=contentDest, src=src, dest=dest)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
