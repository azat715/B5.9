import time
from datetime import timedelta
from functools import reduce, lru_cache, wraps
from itertools import count, takewhile, tee


class Timer:
    """
    вспомогательный класс таймер
    """
    def __init__(self):
        self.t = Timer.timer()
    @staticmethod
    def timer():
        t0 = time.monotonic()
        def stop_timer():
            t1 = time.monotonic()
            return timedelta(seconds = t1 - t0)
        return stop_timer
    def stop(self):
        return self.t()
    @classmethod
    def start(cls):
        return cls()
        

# разные декораторы
# я постарался написать только с использованием только  итераторов и map
# def simple_stopwatch(func):
#     """
#     декоратор который считает время выполнения команды
#     """
#     @wraps(func) # декоратор который запоминает докстринг
#     def wrapper(number):
#         t = Timer.start()
#         res = func(number)
#         return (t.stop(), res)
#     return wrapper

# def round_iter(func):
#     """
#     декоратор который запускает функцию десять раз 
#     """
#     @wraps(func)
#     def wrapper2(number):
#         return map(lambda _: func(number), range(10))
#     return wrapper2

# def round_iter_arg(iters):
#     """
#     декоратор который запускает функцию iters раз 
#     """
#     def decorator(func):
#         @wraps(func)
#         def wrapper(number):
#             return map(lambda _: func(number), range(iters))
#         return wrapper
#     return decorator


# СМОТРЕТЬ ЗДЕСЬ
class Benchmark:
    def __init__(self, iters = 1):
        self.iters = iters # количество итераций
        self.lap_time = None # список значений времени выполнения команды
    
    def __enter__(self):
        self.t2 = Timer.start()
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        print(f"Прошло {self.t2.stop()} секунд")

   
    def __call__(self, func):
        """
        переопределение метода 
        метод __call__ вызывается () как бы всегда перед __init__
        """
        @wraps(func)  # декоратор который запоминает докстринг и прочие атрибуты функции func
        def wrapper(*args, **kwargs):
            s1 = map(lambda _: self.stopwatch(func, *args, **kwargs), range(self.iters))
            res, times = tee(s1) # tee клонирует итератор s1
            self.lap_time = map(lambda x: x[0], times)
            print(f"Среднее значение выполнения программы {func.__name__} в секундах {self.average_time.total_seconds()}")
            print(f"Количество итераций {self.iters}")
            return map(lambda x: x[1], res)
        return wrapper

    def stopwatch(self, func, *args, **kwargs):
        """
        метод который считает время выполнения команды
        """
        self.t1 = Timer.start()
        res = func(*args, **kwargs)
        return (self.t1.stop(), res)
    
    @property
    def average_time(self):
        #return reduce(lambda x, y: x + y, self.lap_time) / self.iters # или sum(self.lap_time, timedelta(seconds=0)
        #  timedelta(seconds=0) - начальное значение для sum 
        return sum(self.lap_time, timedelta(seconds=0)) / self.iters


 #функции дополнительные задержки времени   
def sleep_3s():
    """
    функция эталон - задержка 3 секунды
    """
    time.sleep(3)
    return "Тест работы бенчмарк в контекстном режиме"

"""
@lru_cache(maxsize=32) запоминает результаты работы функции 
если включить то микросекунды, если выключить то секунды 
maxsize - количество значений
"""
@lru_cache(maxsize=32)   
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

# @round_iter_arg(3)
# @simple_stopwatch
@Benchmark(10)
def sum_even(number):
    """
    Функция возвращает сумму четных значений чисел Фибоначчи
    """
    s2 = takewhile(lambda x: x < number, map(fib, count()))
    s3 = filter(lambda x: x % 2 == 0, s2)
    return sum(s3) #reduce(lambda x, y: x + y, s3)

if __name__ == '__main__':
    print("Вариант 1. создаются два экземпляра Benchmark один как декоратор а второй как контекстный менеджер")
    print(sum_even.__doc__) 
    with Benchmark():
        for i in sum_even(4000000):
            print(f"результат {i}")
        sleep_3s()
    
    print("Вариант 2. один экземпляра Benchmark как контекстный менеджер")
    print(sleep_3s.__doc__)
    with Benchmark() as decor:
        decor.iters = 2
        b = decor(sleep_3s)
        for i in b():
            print(i)