import psutil


def exist(n):
    p = filter(lambda v: v.name() == n, psutil.process_iter())[:1]
    return True if p else False

