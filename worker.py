#!/usr/bin/python3
import time
try:
    import queue
except ImportError:
    import Queue as queue
import multiprocessing
from threading import Event
from threading import Thread
from os import getpid
import mapnik


pool = {}


class TileWorker(multiprocessing.Process):

    def __init__(self, mmap, image, job_queue, stop_event):
        multiprocessing.Process.__init__(self)
        self.mmap = mmap
        self.image = image
        self.queue = job_queue
        self.event = stop_event
        # self.job_id = job_id

    def run(self):
        pid = getpid()
        print('{0} starting'.format(pid))
        mapnik.render(self.mmap, self.image)
        print('{0} finished'.format(pid))
        self.queue.put(self.image)
        print('{0} done'.format(pid))
        self.event.set()
        return



def get_tile(mmap, image, result, stop_event):
    print('get_tile begin', getpid())
    mapnik.render(mmap, image)
    print('get_tile end', getpid())
    stop_event.set()
    result['tile'] = image

#
# def RenderTile(job_id, mmap, image):
#     print('RenderTile',getpid())
#     thread_return = {'tile': None}
#     thread = Thread(target=get_tile, args=(mmap, image, thread_return,))
#     pool[job_id] = thread
#     pool[job_id].start()
#     pool[job_id].join()
#     # queue = multiprocessing.Queue()
#     # job_queue = queue.Queue()
#     # process = TileWorker(mmap, image, job_queue)
#     # pool[job_id] = process
#     # process.start()
#     # process.join()
#     # tile = process.get_tile()
#     # del pool[job_id]
#     # image = job_queue.get()
#     print(thread_return['tile'])
#     return thread_return['tile']
#


#
def RenderTile(job_id, mmap, image):
    print('RenderTile',getpid())
    # queue = multiprocessing.Queue()

    result = {'tile': None}
    stop_event = Event()
    thread = Thread(target=get_tile, args=(mmap, image, result, stop_event,))
    pool[job_id] = thread
    pool[job_id].start()
    # pool[job_id].join()
    # while not stop_event.is_set():
        # time.sleep(0.1)
    stop_event.wait()
    return result['tile']

    # job_queue = queue.Queue()
    # stop_event = Event()
    # process = TileWorker(mmap, image, job_queue, stop_event)
    # pool[job_id] = process
    # process.start()
    # # process.join()
    # while not stop_event.is_set():
    #     time.sleep(0.1)
    # del pool[job_id]
    # tile = job_queue.get()
    # return tile



def CancelTileRender(job_id):
    try:
        pool[job_id].terminate()
    except Exception as e:
        print(e)
