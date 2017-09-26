#!/usr/bin/python3
try:
    import queue
except ImportError:
    import Queue as queue
import multiprocessing
from os import getpid
import mapnik


pool = {}


class TileWorker(multiprocessing.Process):

    def __init__(self, mmap, image, job_queue):
        multiprocessing.Process.__init__(self)
        self.mmap = mmap
        self.image = image
        self.queue = job_queue
        # self.job_id = job_id

    def run(self):
        pid = getpid()
        print('{0} starting'.format(pid))
        mapnik.render(self.mmap, self.image)
        print('{0} finished'.format(pid))
        self.queue.put(self.image)
        print('{0} done'.format(pid))
        # print(dir(self))
        # print(self.queue.qsize())
        return


def RenderTile(job_id, mmap, image):
    # queue = multiprocessing.Queue()
    job_queue = queue.Queue()
    process = TileWorker(mmap, image, job_queue)
    pool[job_id] = process
    process.start()
    process.join()
    del pool[job_id]
    image = job_queue.get()
    print(image)
    return image


def CancelTileRender(job_id):
    try:
        pool[job_id].terminate()
    except Exception as e:
        print(e)






# # def TileWorker(render, tile):
# #     pool[getpid()] = self
# #     tile = render()
#
# # https://stackoverflow.com/questions/10415028/how-can-i-recover-the-return-value-of-a-function-passed-to-multiprocessing-proce
# def RenderTile():
#     tile = None
#     worker = multiprocessing.Process(target=TileWorker, args=(render, tile))
#     worker.start()
#     worker.join()
#
# def CancelTile(pid):
#     pool[pid].terminate()
