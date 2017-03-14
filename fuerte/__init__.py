#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>


"""Fuerte Porject

Flask based.
"""

from flask import Flask
from flask import jsonify
from flask_restful import Api
from werkzeug.contrib.fixers import ProxyFix

# Flask Service App
app = Flask(__name__)
app.config.from_object("fuerte.settings.DefaultConfig")
app.config.from_object("fuerte.settings.LogConfig")
app.config.from_object("fuerte.settings.RedisConfig")

# API Service config
from fuerte.api.v1 import controller as v1
api_route = Api(app)
api_route.add_resource(v1.APIView, "/api/v1")


@app.errorhandler(404)
def http_404(error):
    return jsonify(http_code=404,
                   message="Page/API url path not found!"), 404


@app.errorhandler(500)
def http_500(error):
    return jsonify(http_code=500,
                   message="Runtime error(HTTP 500)!"), 500


app.wsgi_app = ProxyFix(app.wsgi_app)
