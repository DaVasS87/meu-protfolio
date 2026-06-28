import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Gestor de Pies (Memória)")

# Inicializar memória
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=['Pie', 'Ativo', 'Qtd', 'Preco'])

# Sidebar
with st.sidebar:
    pie = st.text_input("Nome da Pie", "Minha Pie")
    ativo = st.text_input("Ativo (ex: TTE.PA)", "TTE.PA").upper()
    valor = st.number_input("Valor (€)", value=10.0)
    if st.button("Adicionar"):
        ticker = yf.Ticker(ativo)
        preco = ticker.history(period="1d")['Close'].iloc[-1]
        nova = pd.DataFrame({'Pie': [pie], 'Ativo': [ativo], 'Qtd': [valor/preco], 'Preco': [preco]})
        st.session_state.data = pd.concat([st.session_state.data, nova], ignore_index=True)
        st.rerun()

# Mostrar resultados
st.dataframe(st.session_state.data)

for p in st.session_state.data['Pie'].unique():
    st.subheader(f"Pie: {p}")
    sub = st.session_state.data[st.session_state.data['Pie'] == p]
    st.write(sub)
st.plotly_chart(fig)
    st.info("Portfólio vazio. Usa o pack de operações para começar.")
