import pickle
from ngboost import NGBRegressor
from loguru import logger
import numpy as np

MODEL_PATH = "model.pkl"

def read_model(path: str) -> NGBRegressor:
    with open(path, "rb") as f:
        model, dv = pickle.load(f)
    return model, dv

def get_ci(model: NGBRegressor, X: np.array) -> np.array:
    """Get predictions, and 95% confidence interval for X"""
    z_score = 1.95  # 95% confidence interval
    preds = model.pred_param(X)
    mean = preds[:, 0]
    lower = preds[:, 0] - z_score * np.exp(preds[:, 1])
    upper = preds[:, 0] + z_score * np.exp(preds[:, 1])
    return np.c_[lower, upper]


def handler(event, context) -> dict:
    logger.info("Start predicting")
    logger.info("Reading the model")
    model, dv = read_model(MODEL_PATH)

    X = dv.transform(event)
    logger.info(f"data to predict: {event}")
    ci = get_ci(model, X)
    unlog_ci = np.expm1(ci)
    logger.info(f"Predicted price range: {unlog_ci[0,0]:.2f} - {{unlog_ci[0,1]:.2f}}")
    return {
        "min_price": unlog_ci[0,0],
        "max_price": unlog_ci[0,1]
    }