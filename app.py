import streamlit as st
import yfinance as yf
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Gestor de Portefólio Total", layout="wide")
st.title("📊 Gestor de Portefólio: Estratégia e Execução")

caminho_transacoes = "historico_transacoes.csv"
caminho_metas = "alocacao_desejada.csv"

# Inicialização de arquivos
if not os.path.exists(caminho_transacoes):
    pd.DataFrame(columns=['Data', 'Tipo', 'Ativo', 'Qtd', 'Preco']).to_csv(caminho_transacoes, index=False)
if not os.path.exists(caminho_metas):
    pd.DataFrame(columns=['Ativo', 'Percentagem (%)']).to_csv(caminho_metas, index=False)

df_hist = pd.read_csv(caminho_transacoes)
df_metas = pd.read_csv(caminho_metas)

# --- 1. Sidebar: Estratégia (Alocação) ---
with st.sidebar:
    st.header("🎯 Estratégia de Alocação")
    ativo_alvo = st.selectbox("Ativo:", ["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"])
    pct_alvo = st.slider("Percentagem desejada (%):", 0, 100, 25)
    if st.button("Definir Alocação"):
        df_metas = df_metas[df_metas['Ativo'] != ativo_alvo]
        nova = pd.DataFrame({'Ativo': [ativo_alvo], 'Percentagem (%)': [pct_alvo]})
        df_metas = pd.concat([df_metas, nova], ignore_index=True)
        df_metas.to_csv(caminho_metas, index=False)
        st.rerun()

# --- 2. Expander: Execução (Compra/Venda Pack) ---
with st.expander("🔄 Executar Operações (Pack)"):
    tipo_op = st.radio("Operação:", ["Compra em Pack", "Venda em Pack"], horizontal=True)
    valor_total = st.number_input("Valor total (€):", min_value=0.0, value=500.0)
    ativos_sel = st.multiselect("Ativos:", ["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"], default=["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"])
    
    if st.button("Executar Agora"):
        for ativo in ativos_sel:
            ticker = yf.Ticker(ativo)
            preco = ticker.history(period="1d")['Close'].iloc[-1]
            qtd = valor_total / (len(ativos_sel) * preco)
            tipo = 'Compra' if 'Compra' in tipo_op else 'Venda'
            nova = pd.DataFrame({'Data': [datetime.now().strftime("%Y-%m-%d")], 'Tipo': [tipo], 'Ativo': [ativo], 'Qtd': [qtd], 'Preco': [preco]})
            df_hist = pd.concat([df_hist, nova], ignore_index=True)
        df_hist.to_csv(caminho_transacoes, index=False)
        st.success("Operação concluída!")
        st.rerun()

    if st.button("🚨 RESET TOTAL DO PORTEFÓLIO"):
        if os.path.exists(caminho_transacoes): os.remove(caminho_transacoes)
        if os.path.exists(caminho_metas): os.remove(caminho_metas)
        st.rerun()

# --- 3. Performance e Comparação ---
st.subheader("Performance Atual vs Alocação Desejada")
if not df_hist.empty:
    ativos = df_hist['Ativo'].unique()
    res = []
    total_investido = 0
    
    for a in ativos:
        sub = df_hist[df_hist['Ativo'] == a]
        qtd = sub[sub['Tipo']=='Compra']['Qtd'].sum() - sub[sub['Tipo']=='Venda']['Qtd'].sum()
        if qtd > 0:
            preco = yf.Ticker(a).history(period="1d")['Close'].iloc[-1]
            valor_atual = qtd * preco
            res.append({'Ativo': a, 'Valor Real (€)': valor_atual})
            total_investido += valor_atual
    
    df_res = pd.DataFrame(res)
    df_final = pd.merge(df_res, df_metas, on='Ativo', how='left').fillna(0)
    
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(df_final, use_container_width=True)
    with col2:
        fig = px.pie(df_final, values='Percentagem (%)', names='Ativo', title='Alocação Estratégica (Target)', hole=0.3)
        st.plotly_chart(fig)
        
else:
    st.info("Executa uma operação em pack para começar.")
