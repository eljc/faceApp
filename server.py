from flask import Flask, request, Response, render_template, flash, redirect, url_for

app = Flask(__name__)

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

if __name__ == '__main__':
    # without SSL
   # app.run(debug=True, host='0.0.0.0', threaded=True)

    #  app.run(debug=True, host='0.0.0.0', ssl_context=('example.com+5.pem', 'example.com+5-key.key'))
    # app.run(debug=True, host='0.0.0.0', threaded=True, ssl_context=('ssl/cert.crt', 'ssl/key.key'))

    # app.run(debug=True, host='0.0.0.0', ssl_context='adhoc')
    app.run(ssl_context=("cert.pem", "key.pem"))