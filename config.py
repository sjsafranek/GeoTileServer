#!/usr/bin/python3
import multiprocessing

PORT = 8080
CACHE_DIR = 'cache'
MAX_WORKERS = multiprocessing.cpu_count()
LAYER_DIR = 'examples'
STYLESHEET = 'stylesheet.xml'