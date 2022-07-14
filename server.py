from flask import Flask, request, Response, render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, select
import os
import numpy
import cv2
import api_face


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///face_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)

lista_nomes = []
lista_imagens = []

class Acolhido(db.Model):
    __tablename__ = 'acolhido'
    id_acolhido=db.Column(db.Integer,primary_key=True)
    nome=db.Column(db.String(50),nullable=False)
    nome_foto = db.Column(db.String(50), nullable=False)
    foto = db.Column(db.Text, nullable=False)
    def __repr__(self) :
        value = {
            'id': self.id_acolhido,
            'mome': self.nome,
            'nome_foto': self.nome_foto,
            'foto': self.foto,
        }
        return f"Acolhido(id={self.id_acolhido!r}, nome={self.nome!r}, nome_foto={self.nome_foto!r}, foto={self.foto!r})"

class Registro(db.Model):
    __tablename__ = 'registros'
    id_registro = db.Column(db.Integer, primary_key=True)
    acolhido = db.Column(db.Integer, ForeignKey("acolhido.id_acolhido"))
    data_e_hora_registro = db.Column(db.DateTime)
    def __repr__(self):
        return f"Registro(id={self.id_registro!r}, acolhido={self.acolhido!r}, data_e_hora_registro={self.data_e_hora_registro!r})"


UPLOAD_FOLDER = 'static/images/'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


# for CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    # Put any other methods you need here
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST')
    return response


@app.route('/')
def index():
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
@app.route('/', methods=['POST'])
def upload_file():

    nome = request.form['nome']
    #print(nome)
    

    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('Nenhuma imagem selecionada')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename = nome+'.jpg'                       
        #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))        
        # print('upload_image filename: ' + filename)
        flash('Imagem enviada com sucesso')
        #print('filename', filename)
        #print(app.config['UPLOAD_FOLDER'])
        # gravar imagem ou caminho no banco
        #print('tentar gravar no banco')
        arquivo = app.config['UPLOAD_FOLDER']+filename
        acolhido = Acolhido(nome=nome, nome_foto=filename, foto=arquivo)
        db.session.add(acolhido)
        db.session.commit()
        #fim
        return render_template('index.html', filename=filename)
    else:
        flash('Imagens válidas: - png, jpg, jpeg, gif')
        return redirect(request.url)

@app.route('/display/<filename>', methods=['GET'])
def display_image(filename):
    return redirect(url_for('static', filename='images/' + filename), code=301)

@app.route('/image', methods=['POST'])
def image():
    print('chamada de image')
    global lista_nomes 
    global lista_imagens
    
    faces_codificadas = api_face.obter_imagens_codificadas(lista_imagens)
    #print(faces_codificadas)
    #print('Posicao Lista Geral: ', acolhidos)

    try:
        image_file = request.files['image']  # get the image

        #print("image_file", image_file)

        # Set an image confidence threshold value to limit returned data
        threshold = request.form.get('threshold')
        if threshold is None:
            threshold = 0.5
        else:
            threshold = float(threshold)

        uploadWidth = request.form.get('uploadWidth')
        if uploadWidth is None:
            uploadWidth = 800.0
        else:
            uploadWidth = float(uploadWidth)

        uploadHeight = request.form.get('uploadHeight')
        if uploadHeight is None:
            uploadHeight = 600.0
        else:
            uploadHeight = float(uploadHeight)
        # finally run the image through tensor flow object detection`
        # image_object = cv2.imread('face-images/mike/tuan.jpg')
        image_object = cv2.imdecode(numpy.frombuffer(image_file.read(), numpy.uint8), cv2.IMREAD_UNCHANGED)
        #response = api_face.predict(image_object, threshold, uploadWidth, uploadHeight)

        response = api_face.predict(image_object, threshold, uploadWidth, uploadHeight, faces_codificadas, lista_nomes)

        #print('response', response)
        return response

    except Exception as e:
        #print('POST /image error: %e' % e)
        return e

@app.route('/reconhecer')
def local():
    print('reconhecer')
    statement = select(Acolhido)    
    acolhidos = db.session.execute(statement).all()    
    print('TIPO ACOLHIDOS> ', type(acolhidos))
    global lista_nomes 
    global lista_imagens
    for aco in acolhidos:        
        for a in aco:
            lista_nomes.append(a.nome)
            lista_imagens.append(a.foto)
    
    return render_template('reconhecer.html')

@app.route('/lista')
def lista():
    statement = select(Acolhido.nome, Registro.data_e_hora_registro).join(Registro)

    # list of tuples
    registros  = db.session.execute(statement).all()
    #print(registros)

    return render_template('lista.html')

if __name__ == '__main__':
    # without SSL
   # app.run(debug=True, host='0.0.0.0', threaded=True)

    #  app.run(debug=True, host='0.0.0.0', ssl_context=('example.com+5.pem', 'example.com+5-key.key'))
    # app.run(debug=True, host='0.0.0.0', threaded=True, ssl_context=('ssl/cert.crt', 'ssl/key.key'))

    # app.run(debug=True, host='0.0.0.0', ssl_context='adhoc')
    db.create_all()
    app.run(debug=True, host='0.0.0.0', ssl_context=("certificados/cert.pem", "certificados/key.pem"))