#!/usr/bin/env python
from flask import Flask, Response
from gan_generator import GANGenerator

app = Flask(__name__)

g = GANGenerator("biasfree_14560.cptk")

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

@app.route('/generate/<float:object_space>.obj')
def generate_object_obj(object_space):
    return Response(g.generate_object(object_space, "obj"), status=200, mimetype='text/plain')

@app.route('/generate/<float:object_space>.stl')
def generate_object_stl(object_space):
    return Response(g.generate_object(object_space, "stl"), status=200, mimetype='text/plain')