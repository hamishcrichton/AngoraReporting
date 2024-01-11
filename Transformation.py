import pandas as pd
from MTORFIDList import basic_reporting_query


def transform_date_columns(df):
    for x in [
        "Cutting_Due_Date",
        "Actual_Cutting_Date",
        "Sewing_Due_Date",
        "Actual_Sewing_Date",
        "Bodywork_Due_Date",
        "Actual_Bodywork_Date",
        "Cushioned_Due_Date",
        "Actual_Cushioned_Date",
        "Upholstery_Due_Date",
        "Actual_Upholstery_Date",
        "Metals_Due_Date",
        "Actual_Metals_Date",
        "SHOrigShip",
    ]:

        df.loc[df[x] == "0001-01-01T00:00:00Z", x] = pd.Timestamp('1999-12-31')

        df.loc[df[x] == "0001-01-01", x] = pd.Timestamp('1999-12-31')
        df[x] = df[x].astype(str).str[:10]

        df[x] = pd.to_datetime(df[x], format="%Y-%m-%d").dt.date
    return df
