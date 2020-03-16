from apscheduler.schedulers.background import BackgroundScheduler
from threading import Thread
from typing import List, Callable


class UborzzScheduler(BackgroundScheduler):
    def __init__(self):
        super().__init__()
        self._functions = []

    def new_job(self, fun, *args, **kwargs):
        """Adds a new interval triggered job
        note.
        args will be arguments for the function fun
        kwargs will be arguments for the trigger"""
        print("ARGS", args)
        if not kwargs:
            kwargs = {"hours": 12}
        self.add_job(fun, "interval", args=args, **kwargs)
        self._functions.append((fun, args))

    @staticmethod
    def run(fun: Callable, args: List):
        """Runs function fun in a different thread"""
        worker = Thread(target=fun, args=args)
        worker.setDaemon(True)
        worker.start()

    def run_jobs(self):
        for fun, args in self._functions:
            self.run(fun, args)


scheduler = UborzzScheduler()
