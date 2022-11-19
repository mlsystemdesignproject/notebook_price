import pickle
from ngboost import NGBRegressor
from loguru import logger
import numpy as np

logger.add("logs/predict.log", format="{time} {level} {message}", level="INFO", rotation="10 MB")

MODEL_PATH = "models/ngboost_model.pkl"
sample_data = {'brand_name': 'lenovo',
  'proc_freq': 1.2,
  'proc_brand': 'amd',
  'proc_name': 'amd',
  'proc_count': 2.0,
  'videocard': 'radeon',
  'videocard_memory': 8.0,
  'screen': 11.0,
  'ssd_volume': 0,
  'ram': 4,
  'hdmi': True,
  'material': 'пластик',
  'battery_life': 8.0}
sample_price = np.expm1(10.308952660644293)


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
    return np.c_[mean, lower, upper]


def main():
    logger.info("Start predicting")
    logger.info("Reading the model")
    model, dv = read_model(MODEL_PATH)
    X = dv.transform(sample_data)
    logger.info(f"Sample data: {sample_data}")
    logger.info(f"Sample dat price: {sample_price}")
    logger.info("Evaluating model ...")
    ci = get_ci(model, X)
    logger.info(f"Predicted price: {np.expm1(ci[0,0]):.2f}")
    logger.info(f"95% confidence interval: {np.expm1(ci[0,1]):.2f} - {np.expm1(ci[0,2]):.2f}")


if __name__ == "__main__":
    main()