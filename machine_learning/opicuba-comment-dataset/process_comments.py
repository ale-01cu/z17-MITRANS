import pandas as pd
import os


def combinar_csv_a_excel(ruta_principal, archivo_salida):
    datos_combinados = []

    # Verificar si la ruta principal existe
    if not os.path.exists(ruta_principal):
        print(f"Error: La ruta {ruta_principal} no existe")
        return

    # Crear directorio de salida si no existe
    directorio_salida = os.path.dirname(archivo_salida)
    if directorio_salida and not os.path.exists(directorio_salida):
        os.makedirs(directorio_salida)
        print(f"Se creó el directorio: {directorio_salida}")

    # Iterar sobre todas las carpetas y archivos
    archivos_encontrados = 0
    for root, dirs, files in os.walk(ruta_principal):
        for file in files:
            if file.endswith('.csv'):
                archivos_encontrados += 1
                ruta_completa = os.path.join(root, file)
                try:
                    # Primero intentamos leer el archivo para ver su estructura
                    with open(ruta_completa, 'r', encoding='utf-8') as f:
                        primeras_lineas = [next(f) for _ in range(5) if f]

                    print(f"Analizando archivo: {file}")
                    print(f"Primeras líneas: {primeras_lineas[:2]}")

                    # Intentar diferentes codificaciones y separadores
                    for encoding in ['utf-8', 'latin1', 'cp1252']:
                        for sep in [',', ';', '\t', '|']:
                            try:
                                # Leer el CSV con diferentes parámetros
                                df = pd.read_csv(ruta_completa, encoding=encoding, sep=sep,
                                                 on_bad_lines='skip', engine='python')

                                # Si llegamos aquí, la lectura fue exitosa
                                print(f"Archivo {file} leído con éxito usando encoding={encoding}, sep={sep}")

                                # Verificar y renombrar columnas si es necesario
                                if 'comments' in df.columns:
                                    df.rename(columns={'comments': 'coments'}, inplace=True)
                                elif 'comment' in df.columns:
                                    df.rename(columns={'comment': 'coments'}, inplace=True)

                                # Si no hay columna 'coments' pero hay solo 1 columna, asumimos que es 'coments'
                                if 'coments' not in df.columns and len(df.columns) == 1:
                                    df.rename(columns={df.columns[0]: 'coments'}, inplace=True)
                                    # Crear columna 'label' con valor por defecto
                                    df['label'] = 'sin_clasificar'

                                # Si hay dos columnas pero ninguna es 'coments' o 'label'
                                if len(df.columns) == 2 and ('coments' not in df.columns or 'label' not in df.columns):
                                    df.columns = ['coments', 'label']

                                # Filtrar filas vacías
                                df = df.dropna(subset=['coments'])

                                # Filtrar columnas necesarias
                                if 'coments' in df.columns:
                                    if 'label' in df.columns:
                                        datos_combinados.append(df[['coments', 'label']])
                                    else:
                                        # Si no hay columna 'label', la creamos
                                        df_temp = df[['coments']].copy()
                                        df_temp['label'] = 'sin_clasificar'
                                        datos_combinados.append(df_temp)
                                    break  # Salir del bucle de separadores
                                else:
                                    print(f"Advertencia: {file} no contiene las columnas requeridas")
                            except Exception as e:
                                # print(f"Error con {encoding}, {sep}: {str(e)}")
                                continue  # Probar con el siguiente separador
                        else:
                            continue  # Continuar con la siguiente codificación si ningún separador funcionó
                        break  # Salir del bucle de codificación si un separador funcionó
                    else:
                        # Intento especial para archivos con formato irregular
                        try:
                            # Leer como texto plano y procesar manualmente
                            with open(ruta_completa, 'r', encoding='utf-8') as f:
                                lines = f.readlines()

                            # Crear DataFrame manualmente
                            coments = []
                            labels = []

                            for i, line in enumerate(lines):
                                line = line.strip()
                                if i == 0 and ('comment' in line.lower() or 'label' in line.lower()):
                                    continue  # Saltar encabezado

                                if line and not line.isspace():
                                    coments.append(line)
                                    labels.append('sin_clasificar')

                            if coments:
                                df_manual = pd.DataFrame({'coments': coments, 'label': labels})
                                datos_combinados.append(df_manual)
                                print(f"Archivo {file} procesado manualmente con éxito")
                            else:
                                print(f"Error: No se pudo leer {file} con ninguna combinación de parámetros")
                        except Exception as e:
                            print(f"Error al procesar manualmente {file}: {str(e)}")

                except Exception as e:
                    print(f"Error al procesar {file}: {str(e)}")

    print(f"Total de archivos CSV encontrados: {archivos_encontrados}")

    # Combinar todos los datos
    if datos_combinados:
        df_final = pd.concat(datos_combinados, ignore_index=True)

        # Mostrar información sobre los datos combinados
        print(f"Total de filas combinadas: {len(df_final)}")

        # Guardar en Excel
        try:
            # Verificar si el archivo ya existe
            if os.path.exists(archivo_salida):
                print(f"El archivo {archivo_salida} ya existe. Agregando nuevos datos...")
                # Leer el archivo existente
                df_existente = pd.read_excel(archivo_salida)
                # Combinar con los nuevos datos
                df_final = pd.concat([df_existente, df_final], ignore_index=True)
                # Eliminar duplicados si es necesario
                df_final = df_final.drop_duplicates(subset=['coments'])
                print(f"Total de filas después de combinar con archivo existente: {len(df_final)}")

            # Guardar el resultado final
            df_final.to_excel(archivo_salida, index=False, engine='openpyxl')
            print(f"Archivo creado/actualizado exitosamente: {archivo_salida}")
        except Exception as e:
            print(f"Error al guardar el archivo Excel: {str(e)}")
    else:
        print("No se encontraron datos válidos para procesar")


# Configuración
ruta_principal = r"./input/banco/"  # Ruta absoluta explícita
archivo_salida = r"D:\Z17-MITR\comentarios_combinados.xlsx"

# ruta_principal = r"D:\Z17-MITR\z17-MITRANS-1\machine_learning\opicuba-comment-dataset\input\transporte"  # Ruta absoluta explícita
# archivo_salida = r"D:\Z17-MITR\z17-MITRANS-1\machine_learning\opicuba-comment-dataset\comentarios_combinados11.xlsx"

# Ejecutar función
combinar_csv_a_excel(ruta_principal, archivo_salida)