import pandas as pd

def excel_a_csv(archivo_excel, archivo_csv=None, hoja=0):
    """
    Convierte un archivo Excel a CSV

    Args:
        archivo_excel (str): Ruta del archivo Excel de entrada
        archivo_csv (str, optional): Ruta de salida para el CSV. Si es None,
                                    usa el mismo nombre que el Excel con extensión .csv
        hoja (int/str, optional): Nombre o índice de la hoja a convertir (por defecto: primera hoja)
    """
    # Leer el archivo Excel
    df = pd.read_excel(archivo_excel, sheet_name=hoja)

    # Determinar nombre del archivo CSV si no se especifica
    if archivo_csv is None:
        archivo_csv = archivo_excel.replace('.xlsx', '.csv').replace('.xls', '.csv')

    # Guardar como CSV
    df.to_csv(archivo_csv, index=False, encoding='utf-8')
    print(f"Archivo convertido y guardado como: {archivo_csv}")


# Ejemplo de uso
excel_a_csv('commen (1).xlsx', 'datos_convertidos.csv')