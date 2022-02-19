from os import path

from openpyxl import load_workbook
from pandas import DataFrame, ExcelWriter


def append_df_to_excel(
        df: DataFrame, filename: str, sheet_name='Sheet1',
        **to_excel_kwargs
        ) -> None:
    if not path.exists(filename):
        df.to_excel(
            filename,
            sheet_name=sheet_name,
            **to_excel_kwargs)
        return None
    writer = ExcelWriter(filename, engine='openpyxl', mode='a')
    writer.book = load_workbook(filename)
    start_row = writer.book[sheet_name].max_row
    writer.sheets = {ws.title: ws for ws in writer.book.worksheets}
    df.to_excel(writer, sheet_name, startrow=start_row,
                header=False, **to_excel_kwargs)
    writer.save()
    writer.close()
    return None
