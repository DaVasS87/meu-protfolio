import streamlit as st
import yfinance as yf
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Gestor de Portefólio Real", layout="wide")
st.title("📊 Gestor de Portefólio (Tempo Real)")

caminho_transacoes = "historico_transacoes.csv"

if not os.path.exists(caminho_transacoes):
    pd.DataFrame(columns=['Data', 'Tipo', 'Ativo', 'Qtd', 'Preco']).to_csv(caminho_transacoes, index=False)

df_hist = pd.read_csv(caminho_transacoes)

# --- Sidebar: Reset e Ações ---
with st.sidebar:
    st.header("⚙️ Configurações")
    if st.button("🚨 RESET TOTAL (Apagar tudo)"):
        if os.path.exists(caminho_transacoes):
            os.remove(caminho_transacoes)
            st.rerun()

# --- Expander: Operações em Pack ---
with st.expander("🔄 Operações em Pack (Compra/Venda total)"):
    tipo_op = st.radio("Operação:", ["Compra em Pack", "Venda em Pack"])
    valor_total = st.number_input("Valor total (€):", min_value=0.0, value=500.0)
    ativos_sel = st.multiselect("Ativos:", ["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"], default=["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"])
    
    if st.button("Executar Operação"):
        for ativo in ativos_sel:
            ticker = yf.Ticker(ativo)
            preco = ticker.history(period="1d")['Close'].iloc[-1]
            qtd = valor_total / (len(ativos_sel) * preco)
            tipo = 'Compra' if 'Compra' in tipo_op else 'Venda'
            nova = pd.DataFrame({'Data': [datetime.now().strftime("%Y-%m-%d")], 'Tipo': [tipo], 'Ativo': [ativo], 'Qtd': [qtd], 'Preco': [preco]})
            df_hist = pd.concat([df_hist, nova], ignore_index=True)
        df_hist.to_csv(caminho_transacoes, index=False)
        st.rerun()

# --- Cálculo de Performance e Percentagens Reais ---
st.subheader("Performance Atual")
if not df_hist.empty:
    ativos = df_hist['Ativo'].unique()
    res = []
    total_portefolio = 0
    
    # Calcular valores atuais
    for a in ativos:
        sub = df_hist[df_hist['Ativo'] == a]
        qtd = sub[sub['Tipo']=='Compra']['Qtd'].sum() - sub[sub['Tipo']=='Venda']['Qtd'].sum()
        if qtd > 0:
            preco = yf.Ticker(a).history(period="1d")['Close'].iloc[-1]
            valor_atual = qtd * preco
            res.append({'Ativo': a, 'Qtd': qtd, 'Valor Atual (€)': valor_atual})
            total_portefolio += valor_atual
    
    if res:
        df_res = pd.DataFrame(res)
        # Calcular percentagem real
        df_res['Alocação (%)'] = (df_res['Valor Atual (€)'] / total_portefolio) * 100
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.dataframe(df_res.style.format({'Valor Atual (€)': '{:.2f}', 'Alocação (%)': '{:.2f}%'}), use_container_width=True)
        with col2:
            fig = px.pie(df_res, values='Alocação (%)', names='Ativo', title='Distribuição Real da Carteira (%)', hole=0.3)
            st.plotly_chart(fig)
else:
    st.info("O portefólio está vazio. Executa uma operação em pack.")
