import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)

INPUT_PATH = "data/raw/unfiltered_features.parquet"
OUTPUT_PATH = "data/processed/clean_data.csv"


def replace_rare_category(column: pd.Series, percent: float = 0.05, replace_with: str = "other") -> pd.Series:
    counts = column.value_counts(normalize=True)
    rare_categories = counts[counts < percent].index
    return column.replace(dict.fromkeys(rare_categories, replace_with))


def proc_frequency(proc: str) -> float:
    values = proc.split()
    if values and values[-1] == "ГГц":
        return float(values[-2])
    else:
        return np.NAN


def get_video_memory(column):
    if not column or column == "интегрированная":
        return 0
    values = column.split()
    if values and values[-1].endswith("GB"):
        return int(values[-1].replace("GB", ""))
    else:
        return np.NAN


def get_proc_name(proc: str, popular_names: list = None):
    values = proc.split()
    if not values:
        return np.NAN
    if values[0] == "Intel" and values[1] == "Core":
        result = " ".join(values[0:3])
    else:
        result = " ".join(values[0:2])

    if not popular_names is None:
        if result not in popular_names:
            result = values[0]
    return result


def convert_volume_to_number(val):
    if not val:
        return 0
    num, item = val.split()
    num = int(num)
    if item.lower() == "тб":
        return 1024 * num
    else:
        return num


def fill_na(df: pd.DataFrame) -> pd.DataFrame:
    df_new = df.copy()
    df_new["proc_freq"] = df_new.groupby("proc_brand").proc_freq.transform(lambda x: x.fillna(x.mean()))
    df_new["proc_count"] = df_new.groupby("proc_brand").proc_count.transform(lambda x: x.fillna(x.mean()))
    df_new["videocard_memory"] = df_new.groupby("videocard").videocard_memory.transform(
        lambda x: x.fillna(np.NaN if not x.count() else x.mode()[0]))
    df_new["videocard_memory"] = df_new["videocard_memory"].fillna(0)
    df_new["screen"] = df_new["screen"].fillna(df_new["screen"].mode()[0])
    df_new["material"] = df_new["material"].fillna(df_new["material"].mode()[0])
    df_new["battery_life"] = df_new.groupby("brand_name").battery_life.transform(lambda x: x.fillna(x.mean()))
    return df_new


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    selected_features = [
        "brand_name"
    ]

    df_new = df[selected_features].copy()
    df_new["priceLog"] = np.log1p(df.basePrice)

    df_new["brand_name"] = replace_rare_category(df_new["brand_name"])
    df_new["brand_name"] = df_new["brand_name"].str.lower()

    df_new["proc_freq"] = df["Процессор_Процессор"].apply(proc_frequency)
    df_new["proc_brand"] = df["Процессор_Процессор"].apply(lambda x: x.split()[0])
    df_new["proc_brand"] = df_new["proc_brand"].str.lower()

    proc_names_counts = df["Процессор_Процессор"].apply(get_proc_name).value_counts(normalize=True)
    popular_proc_names = proc_names_counts[proc_names_counts > 0.05].index
    df_new["proc_name"] = df["Процессор_Процессор"].apply(get_proc_name, args=(popular_proc_names,))
    df_new["proc_name"] = df_new["proc_name"].str.lower()

    df_new["proc_count"] = df["Процессор_Количество ядер"]

    df_new["videocard"] = df["Видеокарта_Графический контроллер"]
    df_new.loc[df_new["videocard"].isna(), "videocard"] = "интегрированная"
    df_new.loc[df_new["videocard"].str.contains("Intel"), "videocard"] = "интегрированная"
    df_new.loc[df_new["videocard"].str.contains("UHD Graphics"), "videocard"] = "интегрированная"

    df_new["videocard_memory"] = df_new["videocard"].apply(get_video_memory)

    df_new.loc[df_new["videocard"].str.contains("GeForce RTX"), "videocard"] = "GeForce RTX"
    df_new.loc[df_new["videocard"].str.contains("GeForce GTX"), "videocard"] = "GeForce GTX"
    df_new.loc[df_new["videocard"].str.contains("GeForce MX"), "videocard"] = "GeForce MX"
    df_new.loc[df_new["videocard"].str.contains("Radeon"), "videocard"] = "Radeon"
    df_new["videocard"] = replace_rare_category(df_new["videocard"], percent=0.03)
    df_new["videocard"] = df_new["videocard"].str.lower()

    df_new["screen"] = df["Экран_Диагональ экрана"].apply(lambda x: np.NAN if not x else int(float(x.split('"')[0])))

    df_new["ssd_volume"] = df["Жесткий диск_Объем SSD"].apply(convert_volume_to_number)
    df_new["ram"] = df["Оперативная память_Оперативная память (RAM)"]
    df_new["hdmi"] = ~df["Интерфейсы_Выход HDMI"].isna()

    df_new["material"] = df["Корпус_Материал корпуса"]
    df_new.loc[~df_new["material"].isna() & df_new["material"].str.contains("алюмин|металл|сплав|магний"), "material"] = "металл"
    df_new.loc[~df_new["material"].isna() & df_new["material"].str.contains("пластик|углерод|поликарб"), "material"] = "пластик"

    df_new["battery_life"] = df["Электропитание_Работа от аккумулятора"].apply(lambda x: np.NaN if not x else float(x.split()[1]))

    return df_new



def main():
    logging.info("Start")

    logging.info(f"Reading data from {INPUT_PATH}")
    df = pd.read_parquet(INPUT_PATH)

    logging.info("Cleaning data ...")
    df_new = prepare_data(df)
    df_new = fill_na(df_new)

    logging.info("Saving data ...")
    df_new.to_csv(OUTPUT_PATH, index=False)

    logging.info(f"Data saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
