import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from fpdf import FPDF
import tempfile
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Latitud Solar - Generador de Propuestas", layout="wide")

# --- BASE DE DATOS ---
ciudades_data = {
    "Guayaquil": {"hsp": [4.12, 4.05, 4.38, 4.51, 4.32, 4.10, 4.45, 4.92, 5.15, 5.02, 4.85, 4.58], "temp": 27.5},
    "Durán": {"hsp": [4.08, 3.98, 4.35, 4.48, 4.28, 4.05, 4.40, 4.88, 5.10, 5.05, 4.90, 4.62], "temp": 27.8},
    "Quito": {"hsp": [4.85, 4.62, 4.28, 4.02, 4.15, 4.65, 5.18, 5.42, 5.35, 4.88, 4.55, 4.68], "temp": 14.5},
    "Cuenca": {"hsp": [4.45, 4.38, 4.25, 4.15, 3.85, 3.72, 3.95, 4.35, 4.62, 4.75, 4.82, 4.55], "temp": 15.0}
}

# --- SIDEBAR ---
st.sidebar.header("📋 Datos del Proyecto")
nombre_cliente = st.sidebar.text_input("Cliente", "Martillo Jara Angel Cristobal")
tipo_proyecto = st.sidebar.selectbox("Tipo", ["Comercial", "Residencial"])

# --- LÓGICA DE CÁLCULO ---
ciudad_sel = st.selectbox("📍 Ubicación", list(ciudades_data.keys()))
consumo = st.number_input("Consumo (kWh/mes)", value=1228.0)
planilla = st.number_input("Planilla (USD)", value=149.94)
inv_total = st.number_input("Inversión Total (USD)", value=50013.90)
años_beneficio = st.number_input("Años Beneficio Tributario", min_value=1, max_value=10, value=2)

costo_kwh = planilla / consumo
hsp = sum(ciudades_data[ciudad_sel]["hsp"]) / 12
potencia = consumo / (hsp * 0.82 * 30.44)
gen_y1 = potencia * hsp * 0.82 * 365
ahorro_trib_anual = (inv_total / años_beneficio) if tipo_proyecto == "Comercial" else 0

# Generar Flujo
data_rows, acumulado, payback_exacto = [], 0, None
for a in range(1, 31):
    ahorro_en = gen_y1 * 0.98 * 0.995**(a-1) * costo_kwh
    trib = ahorro_trib_anual if a <= años_beneficio else 0
    total = ahorro_en + trib
    
    if payback_exacto is None and (acumulado + total) >= inv_total:
        payback_exacto = (a - 1) + (inv_total - acumulado) / total
    
    acumulado += total
    data_rows.append({"Año": a, "Ahorro En.": ahorro_en, "Ahorro Trib.": trib, "Total": total, "Acumulado": acumulado})

# --- VISUALIZACIÓN ---
st.metric("Retorno de Inversión (Payback)", f"{payback_exacto:.2f} Años")
st.dataframe(pd.DataFrame(data_rows))

# --- GENERACIÓN PDF ---
def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'PROPUESTA DE RETORNO DE INVERSIÓN', 0, 1, 'C')
    
    pdf.set_font('Arial', '', 11)
    texto = (f"El retorno de inversión estimado es de {payback_exacto:.1f} años. "
             f"Este resultado es el efecto combinado del ahorro energético y el "
             f"escudo fiscal derivado de la depreciación acelerada aplicada en {años_beneficio} año(s). "
             f"Al finalizar este período, el sistema genera un saldo a favor continuo "
             f"para su empresa, maximizando la rentabilidad durante la vida útil del proyecto.")
    pdf.multi_cell(0, 7, texto)
    
    return pdf.output(dest='S').encode('latin-1')

st.download_button("📥 Descargar PDF", data=generar_pdf(), file_name="Propuesta.pdf")
