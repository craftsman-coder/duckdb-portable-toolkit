# %% [markdown]
# # 14 - Run a notebook as a scheduled job

# %%
try:
    import papermill as pm
    pm.execute_notebook(
        input_path="examples/01_basic_queries.py",
        output_path="exports/01_basic_queries_run.ipynb",
        kernel_name="python3",
    )
    print("Notebook executed.")
except Exception as exc:
    print("papermill error:", exc)