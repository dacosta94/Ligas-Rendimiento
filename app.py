import streamlit as st
import pandas as pd
import hashlib
import os
import tempfile

# Función para generar el ID único por jugador
def generar_id(row):
    clave = f"{row['Jugador']}_{row['País de nacimiento']}_{row['Pie']}_{row['Posición específica']}"
    return hashlib.md5(clave.encode()).hexdigest()

# Función para procesar cada archivo cargado
def procesar_archivo_excel(file):
    nombre_liga = os.path.splitext(file.name)[0].upper()
    xls = pd.ExcelFile(file)
    hoja = [s for s in xls.sheet_names if "Search" in s][0]
    df = pd.read_excel(xls, sheet_name=hoja)
    df.fillna('', inplace=True)
    df['ID_Jugador'] = df.apply(generar_id, axis=1)
    df['Liga'] = nombre_liga
    return df

# Título de la app
st.title("🌎 Unificador de Bases - Sudamérica")

st.markdown("""
Sube tus archivos Excel exportados desde Wyscout. Asegúrate de que el **nombre del archivo sea el nombre del país en mayúsculas** (ej: `ECUADOR.xlsx`, `CHILE.xlsx`).
""")

# Carga de múltiples archivos
archivos_cargados = st.file_uploader("📁 Sube los archivos Excel", type=["xlsx"], accept_multiple_files=True)

if archivos_cargados:
    if st.button("🔄 Procesar y Unificar"):
        dataframes = []
        for archivo in archivos_cargados:
            try:
                df = procesar_archivo_excel(archivo)
                dataframes.append(df)
                st.success(f"✔ Procesado: {archivo.name}")
            except Exception as e:
                st.error(f"⚠ Error en {archivo.name}: {e}")

        if dataframes:
            df_final = pd.concat(dataframes, ignore_index=True)
            st.write("✅ Archivos unificados. Vista previa de los primeros registros:")
            st.dataframe(df_final.head(10))

            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                df_final.to_excel(tmp.name, index=False)
                st.download_button(
                    label="📥 Descargar archivo unificado",
                    data=open(tmp.name, 'rb'),
                    file_name="Base_Unificada_Sudamerica.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
