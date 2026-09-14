# %% [markdown]
# # 03 - Schedule a job at a fixed time

# %%
from toolkit.jobs import JobScheduler

# %%
scheduler = JobScheduler()
scheduler.add_cron_job(
    "hello_world",
    lambda: print("Hello from scheduled job!"),
    hour=0, minute=30,
)
scheduler.start()
scheduler.run_now("hello_world")
scheduler.list_jobs()
