# pylint: disable=unused-argument
# pylint: disable=no-value-for-parameter

import os

from utils.utils import (
    concat_list_input_management,
    # read_csv_to_dict,
    main_consultas_sclinico,
)

import click


@click.command()
@click.argument("file_name")
def main(file_name):
    output_dir = "processed"
    os.makedirs(output_dir, exist_ok=True)

    def save_result(df, report_name):
        csv_path = os.path.join(output_dir, f"{report_name}.csv")
        xlsx_path = os.path.join(output_dir, f"{report_name}.xlsx")
        df.to_csv(csv_path, index=False)
        df.to_excel(xlsx_path, index=False)
        print(f"Saved: {csv_path}")
        print(f"Saved: {xlsx_path}")

    if file_name.lower().endswith(".pdf"):
        print(f"Processing {file_name}...")
        df, report_name = main_consultas_sclinico(file_name)
    elif os.path.isdir(file_name):
        pdf_files = [
            os.path.join(file_name, f)
            for f in os.listdir(file_name)
            if f.lower().endswith(".pdf")
        ]
        if not pdf_files:
            print("No PDF files found in the directory.")
            return
        # Use concat_list_input_management to process all PDFs
        df, report_name = concat_list_input_management(
            pdf_files, main_consultas_sclinico
        )

    else:
        print("Please provide a valid PDF file or a directory containing PDF files.")

    df = df.sort_values(by="Data_consulta")

    save_result(df, report_name)


if __name__ == "__main__":
    main()
