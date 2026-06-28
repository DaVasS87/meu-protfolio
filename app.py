import streamlit as st
import yfinance as yf
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Gestão de Portfólio", layout="wide")
st.title("📈 Portfólio: Evolução e Performance")

DATA_FILE = "transacoes.csv"

def inicializar_base():
    dados = [
        {'Data': '2026-06-28', 'Tipo': 'Compra', 'Ativo': 'ALV.DE', 'Qtd': 1, 'Preco_Compra': 71.16},
        {'Data': '2026-06-28', 'Tipo': 'Compra', 'Ativo': 'CVX', 'Qtd': 1, 'Preco_Compra': 63.33},
        {'Data': '2026-06-28', 'Tipo': 'Compra', 'Ativo': 'TTE.PA', 'Qtd': 1, 'Preco_Compra': 60.45},
        {'Data': '2026-06-28', 'Tipo': 'Compra', 'Ativo': 'ZURN.SW', 'Qtd': 1, 'Preco_Compra': 69.77}
    ]
    pd.DataFrame(dados).to_csv(DATA_FILE, index=False)

if not os.path.exists(DATA_FILE):
    inicializar_base()

with st.sidebar:
    st.header("Operações")
    valor_input = st.number_input("Valor (€):", value=10.0)
    ativos_input = st.multiselect("Selecionar ativos:", ["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"])
    if st.button("Comprar Agora"):
        if ativos_input:
            v_por_a = valor_input / len(ativos_input)
            df = pd.read_csv(DATA_FILE)
            for a in ativos_input:
                p = yf.Ticker(a).history(period="1d")['Close'].iloc[-1]
                nova = pd.DataFrame({'Data': [datetime.now().strftime("%Y-%m-%d")], 
                                     'Tipo': ['Compra'], 'Ativo': [a], 
                                     'Qtd': [v_por_a/p], 'Preco_Compra': [p]})
                df = pd.concat([df, nova], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.rerun()
    if st.button("🚨 Reset Total"):
        inicializar_base()
        st.rerun()

st.subheader("Performance Atual")
df_h = pd.read_csv(DATA_FILE)
resumo = []
for a in df_h['Ativo'].unique():
    sub = df_h[df_h['Ativo'] == a]
    q_tot = sub['Qtd'].sum()
    p_med = (sub['Qtd'] * sub['Preco_Compra']).sum() / q_tot
    p_atu = yf.Ticker(a).history(period="1d")['Close'].iloc[-1]
    res = (q_tot * p_atu) - (q_tot * p_med)
    resumo.append({'Ativo': a, 'Investido': round(q_tot*p_med, 2), 'Atual': round(q_tot*p_atu, 2), 'Resultado': round(res, 2)})

df_final = pd.DataFrame(resumo)
st.dataframe(df_final, use_container_width=True)
fig = px.bar(df_final, x='Ativo', y='Resultado', color=df_final['Resultado'] >= 0, color_discrete_map={True: 'green', False: 'red'})
st.plotly_chart(fig)
st.plotly_chart(fig)
    st.info("Portfólio vazio. Usa o pack de operações para começar.")
