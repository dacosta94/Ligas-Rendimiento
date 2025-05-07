import streamlit as st
import pandas as pd
import hashlib
import os
import tempfile

# ========= FUNCIONES =========

def generar_id(row):
    clave = f"{row['Jugador']}_{row['País de nacimiento']}_{row['Pie']}_{row['Posición específica']}"
    return hashlib.md5(clave.encode()).hexdigest()

def procesar_archivo_excel(file):
    nombre_liga = os.path.splitext(file.name)[0].upper()
    xls = pd.ExcelFile(file)
    hoja = [s for s in xls.sheet_names if "Search" in s][0]
    df = pd.read_excel(xls, sheet_name=hoja)
    df.fillna('', inplace=True)
    df['ID_Jugador'] = df.apply(generar_id, axis=1)
    df['Liga'] = nombre_liga
    return df

def calcular_totales_y_ganados(df, columna_base, columna_porcentaje=None):
    if '/90' in columna_base or 'en los 90' in columna_base or 'después de' in columna_base:
        nombre_total = columna_base.split('/90')[0].split(' en los 90')[0].split(' después de')[0].strip()
        df[nombre_total] = (df[columna_base] * df['90s_jugados']).round(0).fillna(0).astype(int)

        if columna_porcentaje:
            if df[columna_porcentaje].dtype == 'object':
                df[columna_porcentaje] = df[columna_porcentaje].str.replace(',', '.').astype(float) / 100
            elif df[columna_porcentaje].dtype in ['int64', 'float64']:
                df[columna_porcentaje] = df[columna_porcentaje] / 100

            nombre_ganado = f"{nombre_total} ganados"
            df[nombre_ganado] = (df[nombre_total] * df[columna_porcentaje]).round(0).fillna(0).astype(int)
            nombre_ganado_90 = f"{nombre_ganado}/90"
            df[nombre_ganado_90] = (df[columna_base] * df[columna_porcentaje]).round(2).fillna(0)
    return df

def procesar_datos_finales(df):
    # Participación en goles
    for col in ['Goles', 'Asistencias', 'Segunda asistencia', 'Tercera asistencia']:
        if col not in df.columns:
            df[col] = 0
    df['Participación en goles'] = df[['Goles', 'Asistencias', 'Segunda asistencia', 'Tercera asistencia']].fillna(0).sum(axis=1)
    df['Participación ponderada'] = df['Goles'] * 1 + df['Asistencias'] * 0.75 + df['Segunda asistencia'] * 0.5 + df['Tercera asistencia'] * 0.25

    # Clasificación de posiciones
    mapa_posiciones = {
        'GK': 'Portero',
        'RB': 'Lateral', 'LB': 'Lateral', 'RWB': 'Lateral', 'LWB': 'Lateral',
        'CB': 'Defensa central', 'LCB': 'Defensa central', 'RCB': 'Defensa central',
        'DM': 'Mediocampista', 'CM': 'Mediocampista', 'RM': 'Mediocampista', 'LM': 'Mediocampista',
        'AM': 'Mediocampista ofensivo', 'RW': 'Mediocampista ofensivo', 'LW': 'Mediocampista ofensivo',
        'SS': 'Delantero', 'CF': 'Delantero', 'LF': 'Delantero', 'RF': 'Delantero'
    }

    def map_pos(pos):
        if isinstance(pos, str):
            pos_split = pos.split(', ')
            if pos_split:
                return mapa_posiciones.get(pos_split[0], 'Otro')
        return 'Otro'

    df['Posición agrupada'] = df['Posición específica'].apply(map_pos)

    def obtener_perfil(pos):
        if isinstance(pos, str):
            pos = pos.upper()
            if pos.startswith('L'):
                return 'Izquierdo'
            elif pos.startswith('R'):
                return 'Derecho'
        return 'Central'

    df['Perfil'] = df['Posición específica'].apply(obtener_perfil)

    if 'Minutos jugados' in df.columns:
        df['% Minutos jugados'] = df['Minutos jugados'] / 540

    # Cálculos por métricas
    if '90s_jugados' in df.columns:
        metricas = [
            ('Acciones defensivas realizadas/90', None),
            ('Duelos/90', 'Duelos ganados, %'),
            ('Regates/90', 'Regates realizados, %'),
            ('Duelos atacantes/90', 'Duelos atacantes ganados, %'),
            ('Pases/90', 'Precisión pases, %'),
            ('Pases hacia adelante/90', 'Precisión pases hacia adelante, %'),
            ('Pases largos/90', 'Precisión pases largos, %'),
            ('Centros/90', 'Precisión centros, %'),
            ('Duelos defensivos/90', 'Duelos defensivos ganados, %'),
            ('Duelos aéreos en los 90', 'Duelos aéreos ganados, %'),
            ('Desmarques/90', 'Precisión desmarques, %'),
            ('Pases en el último tercio/90', 'Precisión pases en el último tercio, %'),
            ('Pases al área de penalti/90', 'Pases hacía el área pequeña, %'),
            ('Pases en profundidad/90', 'Precisión pases en profundidad, %'),
            ('Pases progresivos/90', 'Precisión pases progresivos, %'),
            ('Tiros libres directos/90', 'Tiros libres directos, %'),
            ('Aceleraciones/90', None),
            ('Posesión conquistada después de una entrada', None),
            ('Tiros interceptados/90', None),
            ('Interceptaciones/90', None),
            ('Posesión conquistada después de una interceptación', None),
            ('Faltas/90', None),
            ('Acciones de ataque exitosas/90', None),
            ('xG/90', None),
            ('Toques en el área de penalti/90', None),
            ('Carreras en progresión/90', None),
            ('Centros al área pequeña/90', None),
            ('Pases recibidos /90', None),
            ('Pases largos recibidos/90', None),
            ('Faltas recibidas/90', None),
            ('Jugadas claves/90', None),
            ('Ataque en profundidad/90', None),
            ('Centros desde el último tercio/90', None),
            ('Pases hacía atrás recibidos del arquero/90', None),
            ('Salidas/90', None),
            ('Porterías imbatidas en los 90', None),
            ('Second assists/90', None),
            ('Third assists/90', None),
            ('Tiros libres/90', None),
            ('Córneres/90', None),
            ('Entradas/90', None)
        ]
        for base, porcentaje in metricas:
            if base in df.columns:
                df = calcular_totales_y_ganados(df, base, porcentaje)
    return df

# ========= INTERFAZ STREAMLIT =========

st.title("🌎 Unificador y Procesador de Ligas - Sudamérica")

st.markdown("""
1. Sube archivos Excel exportados desde Wyscout.  
2. Asegúrate de que el **nombre del archivo sea el país en mayúsculas** (ej: `ECUADOR.xlsx`).  
3. El sistema unifica todos los datos y los transforma con métricas avanzadas.
""")

archivos_cargados = st.file_uploader("📁 Sube tus archivos Excel", type=["xlsx"], accept_multiple_files=True)

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
            df_final = procesar_datos_finales(df_final)

            st.write("✅ Archivos procesados. Vista previa:")
            st.dataframe(df_final.head(10))

            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                df_final.to_excel(tmp.name, index=False)
                st.download_button(
                    label="📥 Descargar archivo final procesado",
                    data=open(tmp.name, 'rb'),
                    file_name="Base_Procesada_Sudamerica.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

