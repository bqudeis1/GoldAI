import os
import time
import pandas as pd
from datetime import datetime, timedelta
from dukascopy import Dukascopy

# -------- إعدادات المستخدم --------
INSTRUMENT = "XAUUSD"
TIMEFRAME = "M1"
START_YEAR = 2015
END_YEAR   = 2019  # خمس سنوات
SLEEP_SEC = 2
WEEK_DAYS = 7      # تنزيل أسبوع أسبوع

# اسم الفولدر الذي سيحوي الملفات
DATA_FOLDER = "Gold_Data_XAUUSD"

# إنشاء الفولدر إذا لم يكن موجود
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

duk = Dukascopy()

# -------- دالة لتحديد تاريخ البدء بناء على resume --------
def get_resume_start(year):
    file_name = os.path.join(DATA_FOLDER, f"XAUUSD_M1_{year}.parquet")
    if os.path.exists(file_name):
        df = pd.read_parquet(file_name)
        last_time = pd.to_datetime(df["time"].iloc[-1])
        return last_time + timedelta(minutes=1)
    else:
        return datetime(year, 1, 1)

# -------- دالة لحفظ بيانات الأسبوع في Parquet --------
def save_week_parquet(data, year):
    if not data:
        return
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    file_name = os.path.join(DATA_FOLDER, f"XAUUSD_M1_{year}.parquet")

    # إذا الملف موجود → append بدون header
    if os.path.exists(file_name):
        df.to_parquet(file_name, engine="pyarrow", index=False, append=True)
    else:
        df.to_parquet(file_name, engine="pyarrow", index=False)

# -------- التنزيل الأسبوعي --------
for year in range(START_YEAR, END_YEAR + 1):
    print(f"=== Starting year: {year} ===")
    start_date = get_resume_start(year)
    end_date = datetime(year, 12, 31, 23, 59)

    current = start_date
    while current <= end_date:
        week_end = min(current + timedelta(days=WEEK_DAYS), end_date)

        print(f"Downloading {current} → {week_end}")
        data = duk.get_candles(
            instrument=INSTRUMENT,
            interval=TIMEFRAME,
            start=current,
            end=week_end
        )

        if data:
            save_week_parquet(data, year)

        current = week_end + timedelta(minutes=1)
        time.sleep(SLEEP_SEC)

print(f"All done! Data saved per year in folder: {DATA_FOLDER}")
