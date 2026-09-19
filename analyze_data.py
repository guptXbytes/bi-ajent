import pandas as pd

# Excel files
files = {
    "Deals": "data/deals_Funnel.xlsx",
    "Work Orders": "data/work_Order.xlsx"
}

for name, file_path in files.items():

    print("\n" + "=" * 50)
    print(name.upper())
    print("=" * 50)

    try:
        # Read the Excel file
        excel = pd.ExcelFile(file_path)

        # Check every sheet
        for sheet in excel.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet)

            print(f"\nSheet: {sheet}")
            print("Rows and columns:", df.shape)

            print("\nColumn names:")
            print(df.columns.tolist())

            print("\nFirst 5 rows:")
            print(df.head().to_string(index=False))

    except Exception as error:
        print(f"Error reading {file_path}: {error}")