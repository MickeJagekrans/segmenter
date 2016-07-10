#!/usr/bin/env python3

import os, glob, time, shutil
from flask import Flask, Response, send_from_directory, request
from flask_cors import CORS

from bin import hls_playlist, hls_segment, dash, build_mpd

SOURCE_PATH = glob.glob('media/*.mp4')[0]

app = Flask(__name__, static_folder='static')
CORS(app)

BUILD_QUEUE = []

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def cleanup():
    shutil.rmtree(os.path.join(app.static_folder, 'audio'), True)
    shutil.rmtree(os.path.join(app.static_folder, 'video'), True)
    shutil.rmtree(os.path.join(app.static_folder, 'dash'), True)
    shutil.rmtree('tmp')

@app.route('/Manifest.mpd')
def get_manifest():
    mpd_path = os.path.join('dash', 'Manifest.mpd')
    mpd_static_path = os.path.join(app.static_folder, mpd_path)

    if not os.path.isfile(mpd_static_path):
        mkdir('tmp')
        mkdir(os.path.join(app.static_folder, 'dash'))
        build_mpd.build_mpd(SOURCE_PATH, mpd_static_path)

    return send_from_directory(app.static_folder, mpd_path)

@app.route('/<filename>.mp4')
def get_dash_descriptor(filename):
    index = filename.split('_')[1]
    mpd = os.path.join(app.static_folder, 'dash', '{0}.mpd'.format(index))

    if not index in BUILD_QUEUE and not os.path.isfile(mpd):
        BUILD_QUEUE.append(index)
        dash.build(SOURCE_PATH, index)
        BUILD_QUEUE.remove(index)

    return send_from_directory(app.static_folder, os.path.join('dash', '{0}.mp4'.format(filename)))

@app.route('/<filename>.m4s')
def get_dash_segment(filename):
    index = filename.split('_')[1]
    mpd = os.path.join(app.static_folder, 'dash', '{0}.mpd'.format(index))

    if not index in BUILD_QUEUE and not os.path.isfile(mpd):
        BUILD_QUEUE.append(index)
        dash.build(SOURCE_PATH, index)
        BUILD_QUEUE.remove(index)

    return send_from_directory(app.static_folder, os.path.join('dash', '{0}.m4s'.format(filename)))

@app.route('/crossdomain.xml')
def get_crossdomain():
    return send_from_directory(app.static_folder, 'crossdomain.xml')

@app.route('/hls.m3u8')
def get_master_playlist():
    mkdir(os.path.join(app.static_folder, 'audio'))
    mkdir(os.path.join(app.static_folder, 'video'))
    master = hls_playlist.build_master(SOURCE_PATH)
    return Response(master, mimetype='application/vnd.apple.mpegurl')

@app.route('/<playlist_type>/<bitrate>.m3u8')
def get_playlist(playlist_type, bitrate):
    playlist = hls_playlist.build_playlist(SOURCE_PATH, playlist_type, bitrate)
    hls_segment.segment(SOURCE_PATH, playlist_type, bitrate)
    return Response(playlist, mimetype='application/vnd.apple.mpegurl')

@app.route('/<playlist_type>/<bitrate>/<segno>.ts')
def get_segment(playlist_type, bitrate, segno):
    resource_path = os.path.join(playlist_type, bitrate, '{0}.ts'.format(segno))

    while not os.path.isfile(os.path.join(app.static_folder, resource_path)):
        time.sleep(0.2)

    return send_from_directory(app.static_folder, resource_path)

if __name__ == '__main__':
    cleanup()
    app.run(host="0.0.0.0", port=8080)
