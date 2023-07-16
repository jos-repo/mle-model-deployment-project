import os
from dotenv import load_dotenv
import mlflow
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import make_pipeline


def load_data(year: int, month: int, color: str):
    if not os.path.exists(f"./data/{color}_tripdata_{year}-{month:02d}.parquet"):
        os.system(f"wget -P ./data https://d37ci6vzurychx.cloudfront.net/trip-data/{color}_tripdata_{year}-{month:02d}.parquet")
    df = pd.read_parquet(f"./data/{color}_tripdata_{year}-{month:02d}.parquet")
    return df


def calculate_trip_duration_in_minutes(df: pd.DataFrame, year: int, month: int, color: str):
    df = load_data(year, month, color)
    df["trip_duration_minutes"] = (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 60
    df = df[(df["trip_duration_minutes"] >= 1) & (df["trip_duration_minutes"] <= 60)]
    return df


def preprocess(df: pd.DataFrame, year: int, month: int, color: str):
    df = calculate_trip_duration_in_minutes(df, year, month, color)
    categorical_features = ["PULocationID", "DOLocationID"]
    df[categorical_features] = df[categorical_features].astype(str)
    df['trip_route'] = df["PULocationID"] + "_" + df["DOLocationID"]
    df = df[['trip_route', 'trip_distance', 'trip_duration_minutes']]
    return df


def train(X_train: pd.DataFrame, y_train: pd.DataFrame, X_test: pd.DataFrame, y_test: pd.DataFrame, year: int, month: int, color: str) -> None:
    
    # Set up the connection to MLflow
    load_dotenv()
    MLFLOW_TRACKING_URI=os.getenv("MLFLOW_TRACKING_URI")
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment("yellow-taxi-duration")
    
    # Configure Google Cloud credentials
    SA_KEY=os.getenv("GOOGLE_SA_KEY")
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = SA_KEY
    
    X_train = X_train.to_dict(orient="records")
    X_test = X_test.to_dict(orient="records")

    features = ['PULocationID', 'DOLocationID', 'trip_distance']
    target = 'duration'

    # Check if there is an active run and end it if necessary
    if mlflow.active_run():
        mlflow.end_run()
        
    with mlflow.start_run():    
        tags = {
            "model": "Random Forest Regressor",
            "developer": "Johann",
            "dataset": f"{color}-taxi",
            "year": year,
            "month": month,
            "features": features,
            "target": target
        }
        mlflow.set_tags(tags)

        pipeline = make_pipeline(
            DictVectorizer(),
            RandomForestRegressor(max_depth=10,random_state=42,min_samples_leaf=3)
        )
        pipeline.fit(X_train, y_train)
        
        y_pred = pipeline.predict(X_test)
        rmse = mean_squared_error(y_test, y_pred, squared=False)
        mlflow.log_metric("rmse", rmse)    
        
        mlflow.sklearn.log_model(pipeline, "model")

        # Check for a condition to end the run with a specific status
        #if accuracy > 0.8:
        #    mlflow.end_run(status="FINISHED")  # Change the run status to "FINISHED"
        #else:
        #    mlflow.end_run(status="FAILED")  # Change the run status to "FAILED"


def main():
    year = 2021
    month = 1
    color = "yellow"
    
    df = load_data(year, month, color)
    df = calculate_trip_duration_in_minutes(df, year, month, color)
    df_processed = preprocess(df, year, month, color)
    y=df_processed["trip_duration_minutes"]
    X=df_processed.drop(columns=["trip_duration_minutes"])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    train(X_train, y_train, X_test, y_test, year, month, color)
    
    print("X_train:", X_train.shape)
    print("X_test:", X_test.shape)
    print("y_train:", y_train.shape)
    print("y_test:", y_test.shape)


if __name__ == "__main__":
    main()