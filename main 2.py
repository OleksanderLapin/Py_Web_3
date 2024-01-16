import logging
from collections.abc import Callable, Iterable, Mapping
from time import time
from multiprocessing import cpu_count, Pool
from threading import Thread
from typing import Any

class MyThread(Thread):
    def __init__(self, group: None = None, target: Callable[..., object] | None = None, name: str | None = None, args: Iterable[Any] = ..., kwargs: Mapping[str, Any] | None = None, *, daemon: bool | None = None) -> None:
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.args = args

    def run(self):
        # a, b, c, d = factorize(128, 255, 99999, 10651060)
        logging.debug(factorize(128, 255, 99999, 10651060))
        
# def dev_no_rem(result, number):
#     for i in range(1, int(number ** 0.5) + 1):
#         if i * i == number:
#             result.append(i)
#         elif number % i == 0:
#             result.append(i)
#             result.append(number // i)

def dev_no_rem(result, number):
    for i in range(1, number + 1):
        if number % i == 0:
            result.append(i)


def factorize(*number):
    result = []
    for num in number:
        res = []
        dev_no_rem(res, num)
        res.sort()
        result.append(res)
    return result

def factorize_cpu_bound(*number):
    result = []
    for num in number:
        dev_no_rem(result, num)
    result.sort()
    return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')
    start = time()
    a, b, c, d = factorize(128, 255, 99999, 10651060)
    logging.debug(f'simple: {time() - start}')
    
    with Pool(cpu_count()) as pool:
        start_pool = time()
        a, b, c, d = pool.map(factorize_cpu_bound, (128, 255, 99999, 10651060))
        logging.debug(f'multy: {time() - start_pool}')
    
    assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316, 380395, 532553, 760790, 1065106, 1521580, 2130212, 2662765, 5325530, 10651060]