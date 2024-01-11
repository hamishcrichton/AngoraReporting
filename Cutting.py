import pandas as pd
from datetime import date, timedelta


def to_multi_line(value):
    if isinstance(value, str) and ',' in value:
        return '\n'.join(value.split(', '))
    return value


def manipulate_cutting(df):
    df = df[(df['Cutting_Due_Date'] <= date.today()) & (
                df['Cutting_Due_Date'] > date.today() - timedelta(days=100))]

    df.sort_values(['Priority', 'Cutting_Due_Date'], ascending=[False, True])

    uncut = df[df['Actual_Cutting_Date'] <= date(year=2020, month=1, day=1)]
    uncut = uncut[['Sales_Order_No', 'Model', 'ReadyForCut']].drop_duplicates()
    uncut = pd.pivot_table(uncut, index=['ReadyForCut'], columns=['Model'], values=['Sales_Order_No'], aggfunc=lambda x:list(x)).reset_index()

    cut_progress_in_day = df[df['Cutting_Due_Date'] == date.today()]
    cut_progress_in_day = cut_progress_in_day[['Sales_Order_No', 'Quantity', 'Path', 'Cutting_Due_Date', 'Actual_Cutting_Date', 'CutTime']]
    cut_progress_in_day['Complete'] = cut_progress_in_day['Actual_Cutting_Date'] > date(year=2020, month=1, day=1)
    cut_progress_in_day['Complete'] = cut_progress_in_day.groupby('Sales_Order_No')['Complete'].transform('all')
    cut_progress_in_day = cut_progress_in_day[['Sales_Order_No', 'Complete']]
    cut_progress_in_day = pd.pivot_table(cut_progress_in_day, index=['Complete'], values='Sales_Order_No', aggfunc='nunique').reset_index()

    cut_readiness = df[(df['Actual_Cutting_Date'] <= date(year=2020, month=1, day=1))&(df['Cutting_Due_Date'] == date.today())]
    cut_readiness = pd.pivot_table(cut_readiness, index=['ReadyForCut'], values=['Sales_Order_No'], aggfunc='nunique').reset_index()
    # Assumption: 'uncut' DataFrame needs to be formatted by converting list to comma-separated strings.
    uncut.columns = [col[1] if isinstance(col, tuple) else col for col in uncut.columns]
    uncut.replace({'None': None, 'NaN': None}, inplace=True)
    # The DataFrame has been successfully created by the manipulate_cutting function.
    try:
        uncut = uncut.fillna("None").applymap(lambda x: ', '.join(map(str, x)) if isinstance(x, list) else x)
        uncut = uncut.applymap(to_multi_line)
        uncut.sort_values(by='', ascending=False, inplace=True)
        uncut.replace({True: 'Ready to Cut', False: 'Not Ready to Cut'}, inplace=True)
        uncut.set_index('')
        # uncut.index = uncut.index.map({True: 'Ready to Cut', False: 'Not Ready to Cut'})
    except Exception as e:
        print(f"Failed to format 'uncut' DataFrame: {e}")
        raise e
    return uncut, cut_progress_in_day, cut_readiness
