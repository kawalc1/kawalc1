import os
import psutil

THRESHOLD = 2 * 1024 * 1024


class MemoryUsageMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        mem_before = psutil.Process(os.getpid()).memory_info().rss

        response = self.get_response(request)

        mem_after = psutil.Process(os.getpid()).memory_info().rss
        diff = mem_after - mem_before
        if diff > THRESHOLD:
            print('MEMORY USAGE', diff / 1024 / 1024, request.path)
        return response

