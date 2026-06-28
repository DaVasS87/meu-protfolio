import streamlit as st
import yfinance as yf
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Portefólio de Energia e Seguros", layout="wide")
st.title("📊 Portefólio: Energia e Seguros")

caminho_transacoes = "historico_transacoes.csv"
caminho_metas = "metas_alocacao.csv"

# Garantir arquivos
if not os.path.exists(caminho_transacoes):
    pd.DataFrame(columns=['Data', 'Tipo', 'Ativo', 'Qtd', 'Preco']).to_csv(caminho_transacoes, index=False)
if not os.path.exists(caminho_metas):
    pd.DataFrame(columns=['Ativo', 'Meta']).to_csv(caminho_metas, index=False)

df_hist = pd.read_csv(caminho_transacoes)
df_metas = pd.read_csv(caminho_metas)

# --- Sidebar: Metas ---
with st.sidebar:
    st.header("🎯 Metas de Alocação")
    ativo_meta = st.selectbox("Escolhe o ativo:", ["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"])
    percentagem = st.slider("Percentagem desejada (%):", 0, 100, 25)
    if st.button("Definir Meta"):
        df_metas = df_metas[df_metas['Ativo'] != ativo_meta]
        nova = pd.DataFrame({'Ativo': [ativo_meta], 'Meta': [percentagem]})
        df_metas = pd.concat([df_metas, nova], ignore_index=True)
        df_metas.to_csv(caminho_metas, index=False)
        st.rerun()

# --- Expander: Compra em Pack (O que pediste) ---
with st.expander("➕ Compra em Pack (Dividir capital pelos ativos)"):
    valor_total = st.number_input("Valor total a investir (€):", min_value=0.0, value=500.0)
    ativos_selecionados = st.multiselect("Seleciona os ativos:", ["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"], default=["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"])
    
    if st.button("Executar Compra em Pack"):
        valor_por_ativo = valor_total / len(ativos_selecionados)
        for ativo in ativos_selecionados:
            ticker = yf.Ticker(ativo)
            preco_atual = ticker.history(period="1d")['Close'].iloc[-1]
            qtd = valor_por_ativo / preco_atual
            
            nova_linha = pd.DataFrame({'Data': [datetime.now().strftime("%Y-%m-%d")], 'Tipo': ['Compra'], 'Ativo': [ativo], 'Qtd': [qtd], 'Preco': [preco_atual]})
            df_hist = pd.concat([df_hist, nova_linha], ignore_index=True)
        
        df_hist.to_csv(caminho_transacoes, index=False)
        st.success("Compra efetuada! O capital foi dividido pelos ativos selecionados.")
        st.rerun()

# --- Performance ---
st.subheader("Performance Atual")
if not df_hist.empty or not df_metas.empty:
    # (Lógica de cálculo mantém-se igual...)
    # ...
