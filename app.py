
# A very simple Flask Hello World app for you to get started with...
import os
import shutil
from flask import Flask, render_template, request, url_for, jsonify
from googletrans import Translator, constants
from gradio_client import Client
from datetime import datetime
client = Client("https://facebook-seamless-m4t.hf.space/")

UPLOAD_FOLDER = 'uploads'  # Directory where uploaded files will be stored

# text to text translation using google trans api
translator = Translator(user_agent=constants.DEFAULT_USER_AGENT)
app = Flask(__name__)
app.debug = True  # Enable debug mode
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def home():
    input_text = "" # declaring string variable input text
   
    if request.method == 'POST': #checking if received post request from the form
        input_text = request.form['InputText']
        src_language = request.form['src_language'] #returing form value
        output_text = request.form['OutText'] #returing form value
        output_text = translator.translate(
            input_text, src=src_language, dest="ur").text #calling a google api translate function to translate
        print(input_text) #printing input text for debug purpose 
        return render_template('index.html', input_text=input_text, src_language=src_language, output_text=output_text) # sending value to html 'index.html' file
    else:
        return render_template('index.html')

# end of text to text translation

#start of speech to speech translation

def generate_unique_filename(): # generating unique audio file name 
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    current_time = "src"
    filename = f"audio_{current_time}.wav"
    return filename


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    task = "S2ST (Speech to Speech translation)" # choosing seamless speech to speech model
    input_text = ""
    audio_source = "file" # audio source type
    file_path1 = "uploads/audio_src.wav" # audio file path 
    file_path2 = "uploads/audio_src.wav" # audio file path 

    source_language = "English"
    target_language = "Urdu"
    if 'audio_data' not in request.files:
        return jsonify(status='error', message='No file part')

    file = request.files['audio_data']

    if file.filename == '':
        return jsonify(status='error', message='No selected file')

    if file: # if file found
        filename = generate_unique_filename()  #calling function to generate and return unique file name
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename) #assigning file path 
        file.save(filepath) #saving file to mention path
        src_language = request.form['speech_src_language'] #assigning source language
        trg_language = request.form['trg_language']  #assigning targeted language
        print(src_language) # printing source language for debug purpose 
        print(trg_language) # printing targetted language for debug purpose 
        result = client.predict(
            task,
            audio_source,
            file_path1,
            file_path2,
            input_text,
            src_language,
            trg_language,
            api_name="/run" 
        ) # sending request to seamless api
        print(result)
        print(result[0])

        target_file_path = 'static/uploads/audio_trg.wav' # assinging path to save a audio file
        html_responce = f"<audio controls> <source src='/{target_file_path}' type='audio/wav'> Your browser does not support the audio element.</audio>"

        shutil.move(result[0], target_file_path) #moving the received audio file from seamless to target file path
        jsonify(status='success', message='File uploaded', filename=filename)
        print(f"HTML Response: {html_responce}")  # Add this line for debugging
        gotoindex(html_responce)
        return render_template('index.html', html_responce=html_responce)

@app.route('/', methods=['GET', 'POST'])
def gotoindex(param): # rendering a translated audio
    print('go to index function')
    return render_template('index.html', html_responce=param)

if __name__ == "__main__":
    app.run(debug=True)
