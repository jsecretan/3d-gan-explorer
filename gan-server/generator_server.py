#!/usr/bin/env python
from flask import Flask, Response
from gan_generator import GANGenerator
from functools import lru_cache

app = Flask(__name__)

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

# Caching one is probably the best we can do right now with the hardware we have
@lru_cache(maxsize=1)
def get_generator_for_model(model_name):
	return GANGenerator("models/"+model_name+"/biasfree_998.cptk")

@app.route('/generate/<string:model_name>/<float:object_space>.obj')
def generate_object_obj(model_name, object_space):
    return Response(get_generator_for_model(model_name).generate_object(object_space, "obj"), status=200, mimetype='text/plain')

@app.route('/generate/<string:model_name>/<float:object_space>.stl')
def generate_object_stl(model_name, object_space):
    return Response(get_generator_for_model(model_name).generate_object(object_space, "stl"), status=200, mimetype='text/plain')

# @app.route('/generate/<string:model_name>/<float:object_space>.zip')
# def generate_multiple_obj(model_name, object_space):
# 	return Response(get_generator_for_model(model_name).generate_multiple_objects(object_space), status=200, mimetype='application/zip')
