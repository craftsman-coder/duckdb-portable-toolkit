# %% [markdown]
# # 07 - scikit-learn + MLflow tracking

# %%
import duckdb
import mlflow
from sklearn.ensemble import RandomForestRegressor

from toolkit.ml import init_mlflow, track_run, log_regression_metrics, split

# %%
init_mlflow(experiment="demo-regression")

con = duckdb.connect()
df = con.execute("""
    SELECT
        (i * 2)         AS x1,
        (i % 7)         AS x2,
        (i * 2 + (i % 7) * 3.0 + random() * 0.5) AS y
    FROM range(1, 2001) t(i)
""").fetchdf()

X_train, X_test, y_train, y_test = split(df, target="y", test_size=0.2)

# %%
with track_run("rf-baseline", params={"n_estimators": 100, "max_depth": 6}):
    model = RandomForestRegressor(n_estimators=100, max_depth=6, n_jobs=-1)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    metrics = log_regression_metrics(y_test, preds)
    print(metrics)
    mlflow.sklearn.log_model(model, "model")
