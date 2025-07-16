import pandas as pd
from tabula import read_pdf
from datetime import datetime


def concat_list_input_management(file_names, process):
    # check if only one file was passed
    if not file_names:  # if empty list
        raise ValueError("No file was passed to the function")

    elif len(file_names) == 1:
        # process the file
        df, new_name = process(file_names[0])

        return df, new_name

    # check if more than one file was passe
    else:
        df_list = []
        # metadata_df = pd.DataFrame()

        # create a loop to process each file individually and then concatenate the dataframes and metadata in the end
        for each in file_names:
            # process the file
            df, new_name = process(each)

            # add a new column with the metadata that is different for each file (most of the times is date)
            # df["metadata"] = metadata

            # save the dataframe and metadata in a list
            df_list.append(df)
            # metadata_df = pd.concat([metadata_df, metadata], ignore_index=True)

            # show if there are NA
            # print(df.isna().sum())

        # concatenate the dataframes
        final_df = pd.concat(df_list, ignore_index=True)

        # reset the index
        final_df.reset_index(drop=True, inplace=True)

        # remove duplicates
        final_df.drop_duplicates(inplace=True)

        return final_df, new_name


def read_csv_to_dict(file_path):
    df = pd.read_csv(file_path)
    return dict(zip(df["antigo"], df["novo"]))


def main_consultas_sclinico(file_name):
    print(f"processing {file_name}")

    # temporary report name since metadata is not being extracted yet
    report_name = "consultas_sclinico"
    # report_name = file_name

    print(f"reading pdf file {file_name}")

    # read pdf file with tabula
    tables = read_pdf(file_name, pages="all")

    # tables is a list of dataframes where each dataframe is a table that will be merged by the end
    column_names_11 = [
        "Data",
        "Hora",
        "Tipo_consutlta",
        "Nome_utente",
        "Número_utente",
        "Data_nascimento",
        "Local",
        "Meio_realização",
        "Iniciativa",
        "Forma_marcação",
        "Estado",
    ]
    column_names_10 = [
        "Data",
        "Hora",
        "Tipo_consutlta",
        "Nome_utente",
        "Número_utente",
        "Data_nascimento",
        "Local",
        "Meio_realização",
        "Iniciativa",
        "Forma_marcação",
    ]  # , "Estado"]

    print("creating initil dataframe")

    # create a dataframe with the columns
    df = pd.DataFrame(columns=column_names_11)

    print("concatenating tables")

    for table in tables:
        table = pd.DataFrame(table)
        if table.shape[1] == 10:
            table.columns = column_names_10
        elif table.shape[1] == 11:
            table.columns = column_names_11

        # some rows have empty values in the first column, we will remove
        # table = table[table["Data"].notnull()]
        # Filter out empty or all-NA columns from the table
        # table_filtered = table.dropna(axis=1, how='all')

        print("concatenating table")

        # Exclude empty or all-NA entries before concatenation
        df = pd.concat(
            [df.dropna(how="all", axis=1), table.dropna(how="all", axis=1)],
            ignore_index=True,
        )

    print("table concatenated. initial processing")

    # remove rows with "Nome_utente" values as NaN
    df = df[df["Nome_utente"].notnull()]

    print("second line processing")

    # por vezes uma linha é dividida em duas porque um Nome_utente ficou numa linha e o resto na linha seguinte, sendo que a linha seguinte fica com os restantes campos vazios, Nome_utenteadamente a data
    # vamos concatenar o Nome_utente de uma linha que não tenha data com a linha anterior e apagar essa linha inicial
    for i, row in df.iterrows():
        try:
            if pd.isnull(row["Data"]):
                df.loc[i - 1, "Nome_utente"] = (
                    df.loc[i - 1, "Nome_utente"] + " " + row["Nome_utente"]
                )
        except KeyError:
            print("KeyError")

    df = df[df["Data"].notnull()]

    print("Processing Nome: capiltalize")

    # "Nome_utente" with capital 1st letters
    df["Nome_utente"] = df["Nome_utente"].str.title()

    # print the unique values in the "Tipo_consutlta" column before substitution
    # print("\n".join(df["Tipo_consutlta"].unique()))

    print("renaming and hamonizing names of tipo_consulta")

    # substitute the values in the "Tipo_consutlta" column
    sub_consulta_dict = read_csv_to_dict("dicionario_tipo_consultas_sclinico.csv")
    df["Tipo_consutlta"] = df["Tipo_consutlta"].replace(sub_consulta_dict)

    # print the unique values in the "Tipo_consutlta" column after substitution
    # print("\n".join(df["Tipo_consutlta"].unique()))

    print("corecting values in the 'Meio_realização' column")

    subs_tipo_contacto = {"Telefone ou": "Teleconsulta", "Através do": "Secretariado"}

    df["Meio_realização"] = df["Meio_realização"].replace(subs_tipo_contacto)

    # se coluna "Forma_marcação" tiver valores "Telefone Realizado"
    # substituir "Forma_marcação" por "Telefone"
    # e Estado para "Realizado"

    print("correcting values in the 'Forma_marcação' column")

    df.loc[df["Forma_marcação"] == "Telefone Realizado", "Estado"] = "Realizado"
    df.loc[df["Forma_marcação"] == "Telefone Realizado", "Forma_marcação"] = "Telefone"

    df.loc[df["Forma_marcação"] == "PresenciaRealizado", "Estado"] = "Realizado"
    df.loc[
        df["Forma_marcação"] == "PresenciaRealizado", "Forma_marcação"
    ] = "Presencial"

    df.loc[df["Forma_marcação"] == "Realizado", "Estado"] = "Realizado"
    df.loc[df["Forma_marcação"] == "Realizado", "Forma_marcação"] = None

    df.loc[df["Forma_marcação"] == "E-mail Realizado", "Estado"] = "Realizado"
    df.loc[df["Forma_marcação"] == "E-mail Realizado", "Forma_marcação"] = "E-mail"

    # calcular idade da pessoa na data da conuslta

    print("calculating age at the time of consultation")

    # Convert columns to datetime
    df["Data_nascimento"] = pd.to_datetime(df["Data_nascimento"], format="%d-%m-%Y")
    df["Data"] = pd.to_datetime(df["Data"], format="%d-%m-%Y")
    # Combine "Data" and "Hora" columns into a new datetime column
    df["Data_consulta"] = df.apply(
        lambda row: (
            datetime.combine(
                row["Data"], datetime.strptime(row["Hora"], "%H:%M").time()
            )
            if pd.notnull(row["Data"]) and pd.notnull(row["Hora"])
            else None
        ),
        axis=1,
    )

    # Calculate age at the time of consultation
    df["Idade_consulta"] = df.apply(
        lambda row: (
            (row["Data"] - row["Data_nascimento"]).days // 365
            if pd.notnull(row["Data"]) and pd.notnull(row["Data_nascimento"])
            else None
        ),
        axis=1,
    )
    df["Idade_dias_consulta"] = df.apply(
        lambda row: (
            (row["Data"] - row["Data_nascimento"]).days
            if pd.notnull(row["Data"]) and pd.notnull(row["Data_nascimento"])
            else None
        ),
        axis=1,
    )

    # Calculate age at november 8th 2024
    # df["Idade_8_nov"] = df.apply(lambda row: (datetime(2024, 11, 8) - row["Data_nascimento"]).days // 365 if pd.notnull(row["Data_nascimento"]) else None, axis=1)
    # df["Idade_dias_8_nov"] = df.apply(lambda row: (datetime(2024, 11, 8) - row["Data_nascimento"]).days if pd.notnull(row["Data_nascimento"]) else None, axis=1)

    print("calculating age in months at the time of consultation")

    # calculata age in months if idade < 2 years
    df["Idade_meses_consulta"] = df.apply(
        lambda row: (
            (row["Data"] - row["Data_nascimento"]).days // 30
            if pd.notnull(row["Data"])
            and pd.notnull(row["Data_nascimento"])
            and (row["Data"] - row["Data_nascimento"]).days // 365 < 2
            else None
        ),
        axis=1,
    )
    df["Idade_meses_8_nov"] = df.apply(
        lambda row: (
            (datetime(2024, 11, 8) - row["Data_nascimento"]).days // 30
            if pd.notnull(row["Data_nascimento"])
            and (datetime(2024, 11, 8) - row["Data_nascimento"]).days // 365 < 2
            else None
        ),
        axis=1,
    )

    print("tidying up dataframe")

    # reset index
    df.reset_index(drop=True, inplace=True)

    # order columns by its name
    df = df[
        [
            "Data_consulta",
            "Data",
            "Hora",
            "Tipo_consutlta",
            "Nome_utente",
            "Número_utente",
            "Data_nascimento",
            "Idade_consulta",
            "Idade_dias_consulta",
            "Idade_meses_consulta",
            "Local",
            "Meio_realização",
            "Iniciativa",
            "Forma_marcação",
            "Estado",
        ]
    ]

    print("renaming columns")

    # rename columns Número_utenteto Utente
    df.rename(
        columns={
            "Número_utente": "Utente",
            "Nome_utente": "Nome",
        },
        inplace=True,
    )

    print("make shure columns are in the right format")

    # make Número_utente int
    df["Utente"] = df["Utente"].astype(int)

    print("processing finished")

    return df, report_name
