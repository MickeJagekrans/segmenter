#!/usr/bin/env python

import os, glob
from flask import Flask, Response, send_from_directory, request
from flask_cors import CORS

from bin import hls_playlist, hls_segment

SOURCE_PATH = glob.glob('media/*.mp4')[0]

app = Flask(__name__, static_folder='static')
CORS(app)

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

#@app.route('/Manifest.mpd')

@app.route('/hls.m3u8')
def get_master_playlist():
    master = hls_playlist.build_master(SOURCE_PATH)
    return Response(master, mimetype='application/vnd.apple.mpegurl')

@app.route('/crossdomain.xml')
def get_crossdomain():
    return send_from_directory(app.static_folder, 'crossdomain.xml')

@app.route('/<playlist_type>/<bitrate>.m3u8')
def get_playlist(playlist_type, bitrate):
    playlist = hls_playlist.build_playlist(SOURCE_PATH, playlist_type, bitrate)
    return Response(playlist, mimetype='application/vnd.apple.mpegurl')

@app.route('/<playlist_type>/<bitrate>/<segno>.ts')
def get_segment(playlist_type, bitrate, segno):
    resource_path = os.path.join(playlist_type, bitrate, '{0}.ts'.format(segno))

    if not os.path.isfile(os.path.join(app.static_folder, resource_path)):
        hls_segment.transmux(SOURCE_PATH, playlist_type, bitrate, int(segno))

    return send_from_directory(app.static_folder, resource_path)

if __name__ == '__main__':
    mkdir('static')
    mkdir('static/audio')
    mkdir('static/video')
    app.run(host="0.0.0.0", port=8080)
