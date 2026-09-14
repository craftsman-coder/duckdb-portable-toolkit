"""Pure-Python job scheduler using APScheduler."""

from __future__ import annotations

import importlib.util
import traceback
from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from toolkit.config import LOGS_DIR, scheduler_cfg


class JobScheduler:
    def __init__(self, log_dir=None):
        self.log_dir = Path(log_dir) if log_dir else LOGS_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._scheduler = BackgroundScheduler(
            timezone=scheduler_cfg().get("timezone", "UTC")
        )

    def _log(self, job_name, message):
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{stamp}] [{job_name}] {message}"
        print(line)
        with open(self.log_dir / f"{job_name}.log", "a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def _wrap(self, name, func):
        def runner():
            self._log(name, "start")
            try:
                func()
                self._log(name, "done")
            except Exception:
                self._log(name, "FAILED\n" + traceback.format_exc())
        return runner

    @staticmethod
    def _load_from_file(path):
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(path)
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not hasattr(module, "run"):
            raise AttributeError(f"{path} must define a run() function")
        return module.run

    def _resolve(self, target):
        return target if callable(target) else self._load_from_file(target)

    def add_cron_job(self, name, target, *, hour=0, minute=0,
                     day_of_week=None, day=None, month=None):
        func = self._wrap(name, self._resolve(target))
        trigger = CronTrigger(hour=hour, minute=minute,
                              day_of_week=day_of_week, day=day, month=month)
        self._scheduler.add_job(func, trigger=trigger, id=name, replace_existing=True)
        print(f"  registered cron job '{name}'")
        return self

    def add_interval_job(self, name, target, *, seconds=0, minutes=0, hours=0):
        func = self._wrap(name, self._resolve(target))
        trigger = IntervalTrigger(seconds=seconds, minutes=minutes, hours=hours)
        self._scheduler.add_job(func, trigger=trigger, id=name, replace_existing=True)
        print(f"  registered interval job '{name}'")
        return self

    def start(self):
        if self._scheduler.running:
            print("  scheduler already running"); return
        self._scheduler.start()
        print("  scheduler started (background thread)")

    def stop(self):
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
        print("  scheduler stopped")

    def run_now(self, name):
        job = self._scheduler.get_job(name)
        if job is None:
            print(f"  job '{name}' not found"); return
        job.func()

    def list_jobs(self):
        return [{"id": j.id, "next_run": str(j.next_run_time),
                 "trigger": str(j.trigger)} for j in self._scheduler.get_jobs()]
