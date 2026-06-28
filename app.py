import streamlit as st
import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# 1. Setup
st.set_page_config(layout="wide")
st.title("📈 Portfólio Evolutivo")
FILE = "transacoes.csv"

# 2. Base de Dados
def init():
    d = [{'Data': '2026-06-28', 'Tipo': 'Compra', 'Ativo': 'ALV.DE', 'Qtd': 1, 'Preco_Compra': 71.16},
         {'Data': '2026-06-28', 'Tipo': 'Compra', 'Ativo': 'CVX', 'Qtd': 1, 'Preco_Compra': 63.33},
         {'Data': '2026-06-28', 'Tipo': 'Compra', 'Ativo': 'TTE.PA', 'Qtd': 1, 'Preco_Compra': 60.45},
         {'Data': '2026-06-28', 'Tipo': 'Compra', 'Ativo': 'ZURN.SW', 'Qtd': 1, 'Preco_Compra': 69.77}]
    pd.DataFrame(d).to_csv(FILE, index=False)

if not os.path.exists(FILE):
    init()

# 3. Sidebar (Operações)
with st.sidebar:
    st.header("Operações")
    valor = st.number_input("Valor (€):", value=10.0)
    ativos = st.multiselect("Ativos:", ["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"])
    if st.button("Comprar"):
        df = pd.read_csv(FILE)
        for a in ativos:
            p = yf.Ticker(a).history(period="1d")['Close'].iloc[-1]
            nova = pd.DataFrame({'Data': [datetime.now().strftime("%Y-%m-%d")], 'Tipo': ['Compra'], 'Ativo': [a], 'Qtd': [(valor/len(ativos))/p], 'Preco_Compra': [p]})
            df = pd.concat([df, nova], ignore_index=True)
        df.to_csv(FILE, index=False)
        st.rerun()

# 4. Performance
st.subheader("Performance")
df = pd.read_csv(FILE)
res = []
for a in df['Ativo'].unique():
    sub = df[df['Ativo'] == a]
    q_tot = sub['Qtd'].sum()
    pm = (sub['Qtd'] * sub['Preco_Compra']).sum() / q_tot
    p_atu = yf.Ticker(a).history(period="1d")['Close'].iloc[-1]
    res.append({'Ativo': a, 'Lucro_Prejuizo': round((q_tot * p_atu) - (q_tot * pm), 2)})

st.dataframe(pd.DataFrame(res))
st.bar_chart(pd.DataFrame(res).set_index('Ativo'))
st.plotly_chart(fig)
    st.info("Portfólio vazio. Usa o pack de operações para começar.")
