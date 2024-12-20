# Import the built-in libraries
import os
import sys
import time
import zipfile
import glob
import threading

import eventlet
eventlet.monkey_patch()

# Import external libraries
import numpy as np
from flask import Flask, render_template, url_for, request, send_file, abort
from flask_socketio import SocketIO, emit, disconnect

# Import customized libraries
from config import flask_config, flask_folder
from routes import my_routes
from src.utils.downloader import BGPLiveDataCapturer

# Load Flask configuration
async_mode, app, socketio, thread, thread_lock = flask_config()
flask_folder()

# register the routes
app.register_blueprint(my_routes)

# 创建BGP实时数据捕获器
live_capturer = BGPLiveDataCapturer(socketio)

@socketio.on('connect', namespace='/bgp')
def handle_connect():
    """处理WebSocket连接"""
    emit('connection_response', {'status': 'connected'})

@socketio.on('start_capture', namespace='/bgp')
def handle_start_capture(data):
    """处理开始捕获请求"""
    try:
        filters = data.get('filters', {})
        live_capturer.start_capture(filters)
        emit('capture_started', {
            'status': 'success',
            'filters': filters
        })
    except Exception as e:
        emit('capture_error', {'error': str(e)})

@socketio.on('stop_capture', namespace='/bgp')
def handle_stop_capture():
    """处理停止捕获请求"""
    try:
        live_capturer.stop_capture()
        emit('capture_stopped', {'status': 'success'})
    except Exception as e:
        emit('capture_error', {'error': str(e)})

@socketio.on('get_status', namespace='/bgp')
def handle_get_status():
    """获取捕获状态"""
    try:
        status = live_capturer.get_status()
        emit('capture_status', status)
    except Exception as e:
        emit('capture_error', {'error': str(e)})

# You can use socketio to create websockets

"""
## Launch app
"""
if __name__ == '__main__':
    socketio.run(
        app, 
        debug=True, 
        host='0.0.0.0',
        port=5000
    )
    # app.run(debug=True)