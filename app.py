import streamlit as st
import yfinance as yf
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📈 Portfólio")

DATA_FILE = "transacoes.csv"

def init_base():
    d = [{'Data': '2026-06-28', 'Tipo': 'Compra', 'Ativo': 'ALV.DE', 'Qtd': 1, 'Preco_Compra': 71.16},
         {'Data': '2026-06-28', 'Tipo': 'Compra', 'Ativo': 'CVX', 'Qtd': 1, 'Preco_Compra': 63.33},
         {'Data': '2026-06-28', 'Tipo': 'Compra', 'Ativo': 'TTE.PA', 'Qtd': 1, 'Preco_Compra': 60.45},
         {'Data': '2026-06-28', 'Tipo': 'Compra', 'Ativo': 'ZURN.SW', 'Qtd': 1, 'Preco_Compra': 69.77}]
    pd.DataFrame(d).to_csv(DATA_FILE, index=False)

if not os.path.exists(DATA_FILE):
    init_base()

with st.sidebar:
    v_in = st.number_input("Valor (€):", value=10.0)
    a_in = st.multiselect("Ativos:", ["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"])
    if st.button("Comprar"):
        if a_in:
            v_p_a = v_in / len(a_in)
            df = pd.read_csv(DATA_FILE)
            for a in a_in:
                p = yf.Ticker(a).history(period="1d")['Close'].iloc[-1]
                nova = pd.DataFrame({'Data': [datetime.now().strftime("%Y-%m-%d")], 'Tipo': ['Compra'], 'Ativo': [a], 'Qtd': [v_p_a/p], 'Preco_Compra': [p]})
                df = pd.concat([df, nova], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.rerun()
    if st.button("Reset"):
        init_base()
        st.rerun()

st.subheader("Performance")
df = pd.read_csv(DATA_FILE)
res = []
for a in df['Ativo'].unique():
    sub = df[df['Ativo'] == a]
    q = sub['Qtd'].sum()
    pm = (sub['Qtd'] * sub['Preco_Compra']).sum() / q
    pa = yf.Ticker(a).history(period="1d")['Close'].iloc[-1]
    res.append({'Ativo': a, 'Resultado': round((q * pa) - (q * pm), 2)})

df_f = pd.DataFrame(res)
st.dataframe(df_f)
st.bar_chart(df_f.set_index('Ativo'))
st.plotly_chart(fig)
    st.info("Portfólio vazio. Usa o pack de operações para começar.")
