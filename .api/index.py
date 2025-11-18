from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/hola")
def hola():
    return jsonify({"mensaje": "Hola mundo"})

# Esto hace que funcione con Vercel serverless
def handler(request, response):
    from werkzeug.wrappers import Request, Response
    req = Request(request.environ)
    resp = Response()
    with app.test_request_context(req.path):
        rv = app.full_dispatch_request()
        resp.data = rv.get_data()
        resp.status_code = rv.status_code
        for k, v in rv.headers.items():
            resp.headers[k] = v
    return resp
