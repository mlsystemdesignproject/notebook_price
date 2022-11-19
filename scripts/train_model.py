import pickle

import pandas as pd
import numpy as np
from loguru import logger
from sklearn.feature_extraction import DictVectorizer
from ngboost import NGBRegressor
from ngboost.distns import Normal
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error

logger.add("logs/train.log", format="{time} {level} {message}", level="INFO", rotation="10 MB")

INPUT_PATH = "data/processed/clean_data.csv"
MODEL_PATH = "models/ngboost_model.pkl"


def read_data() -> pd.DataFrame:
    """Read data from INPUT_PATH"""
    df = pd.read_csv(INPUT_PATH)
    y = df["priceLog"]
    X = df.drop("priceLog", axis=1)
    logger.info(f"Data read. X shape: {X.shape}, y shape: {y.shape}")
    logger.info(f"X columns: {X.columns}")
    return X, y


def get_model() -> NGBRegressor:
    logger.info("Creating model")
    model = NGBRegressor(
        Dist=Normal,
        verbose=False,
        n_estimators=2000
    )
    return model


def cross_validation_score(model: NGBRegressor, X: np.array, y: np.array) -> None:
    """Calculate cross validation score for model"""
    result = list(np.round((-cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error')) ** 0.5, 5))
    logger.info(f"Cross validation RMSE for {model}")
    logger.info(f"cv_results: {result}")
    logger.info(f"Mean RMSE: {np.mean(result):.5f}")


def get_ci(model: NGBRegressor, X: np.array) -> np.array:
    """Get predictions, and 95% confidence interval for X"""
    z_score = 1.95  # 95% confidence interval
    preds = model.pred_param(X)
    mean = preds[:, 0]
    lower = preds[:, 0] - z_score * np.exp(preds[:, 1])
    upper = preds[:, 0] + z_score * np.exp(preds[:, 1])
    return np.c_[mean, lower, upper]


def ci_train_score(model: NGBRegressor, X: np.array, y: np.array) -> None:
    """Calculate train RMSE and 95% confidence interval for model"""
    ci = get_ci(model, X)
    logger.info(f"Train RMSE = {mean_squared_error(model.predict(X), y) ** 0.5:2f}")
    y_in_ci_mean = np.mean((ci[:, 1] < y) & (ci[:, 2] > y))
    logger.info(f"Mean y in CI: {y_in_ci_mean:.3f}")


def main():
    logger.info("Start training NGBoost model")
    logger.info("Reading data")
    X, y = read_data()

    dv = DictVectorizer(sparse=False)
    X = dv.fit_transform(X.to_dict(orient="records"))

    model = get_model()
    cross_validation_score(model, X, y)

    model.fit(X, y)
    ci_train_score(model, X, y)

    logger.info("Saving model")
    with open(MODEL_PATH, "wb") as f:
        pickle.dump((model, dv), f)
        logger.success("Model saved")


if __name__ == "__main__":
    main()
