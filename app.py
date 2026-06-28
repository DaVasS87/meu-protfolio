import streamlit as st
import yfinance as yf
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

# Configuração Global
st.set_page_config(page_title="App de Gestão de Portefólio", layout="wide")
st.title("📈 App de Gestão de Portefólio: Completa")

# Arquivos de Dados
DATA_FILE = "transacoes.csv"
META_FILE = "alocacao.csv"

# Garantir persistência
if not os.path.exists(DATA_FILE): pd.DataFrame(columns=['Data', 'Tipo', 'Ativo', 'Qtd', 'Preco']).to_csv(DATA_FILE, index=False)
if not os.path.exists(META_FILE): pd.DataFrame(columns=['Ativo', 'Percentagem (%)']).to_csv(META_FILE, index=False)

# --- SIDEBAR: Configuração e Alocação ---
with st.sidebar:
    st.header("⚙️ Configurações")
    st.subheader("🎯 Definir Alocação Estratégica")
    ativo_alvo = st.selectbox("Ativo para Alocação:", ["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"])
    pct_alvo = st.slider("Percentagem desejada (%):", 0, 100, 25)
    if st.button("Gravar Estratégia"):
        df_metas = pd.read_csv(META_FILE)
        df_metas = df_metas[df_metas['Ativo'] != ativo_alvo]
        nova = pd.DataFrame({'Ativo': [ativo_alvo], 'Percentagem (%)': [pct_alvo]})
        pd.concat([df_metas, nova], ignore_index=True).to_csv(META_FILE, index=False)
        st.success("Alocação gravada!")
    
    st.divider()
    if st.button("🚨 RESET TOTAL DO PORTFÓLIO"):
        if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
        if os.path.exists(META_FILE): os.remove(META_FILE)
        st.rerun()

# --- EXPANDERS DE EXECUÇÃO ---
col1, col2 = st.columns(2)

with col1:
    with st.expander("➕ Compra/Venda em Pack"):
        tipo_op = st.radio("Operação:", ["Compra", "Venda"], horizontal=True)
        valor_total = st.number_input("Montante Total (€):", min_value=0.0, value=500.0)
        ativos_sel = st.multiselect("Seleciona Ativos:", ["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"], default=["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"])
        
        if st.button("Executar Pack"):
            df_hist = pd.read_csv(DATA_FILE)
            for ativo in ativos_sel:
                preco = yf.Ticker(ativo).history(period="1d")['Close'].iloc[-1]
                qtd = valor_total / (len(ativos_sel) * preco)
                nova = pd.DataFrame({'Data': [datetime.now().strftime("%Y-%m-%d")], 'Tipo': [tipo_op], 'Ativo': [ativo], 'Qtd': [qtd], 'Preco': [preco]})
                df_hist = pd.concat([df_hist, nova], ignore_index=True)
            df_hist.to_csv(DATA_FILE, index=False)
            st.rerun()

# --- PERFORMANCE E VISUALIZAÇÃO ---
st.subheader("Performance e Distribuição")
df_hist = pd.read_csv(DATA_FILE)
df_metas = pd.read_csv(META_FILE)

if not df_hist.empty:
    res = []
    for a in df_hist['Ativo'].unique():
        sub = df_hist[df_hist['Ativo'] == a]
        qtd = sub[sub['Tipo']=='Compra']['Qtd'].sum() - sub[sub['Tipo']=='Venda']['Qtd'].sum()
        if qtd > 0:
            preco = yf.Ticker(a).history(period="1d")['Close'].iloc[-1]
            res.append({'Ativo': a, 'Quantidade': round(qtd, 4), 'Valor Atual (€)': round(qtd * preco, 2)})
    
    df_res = pd.DataFrame(res)
    
    # Exibir Tabela e Gráfico
    c1, c2 = st.columns(2)
    with c1:
        st.dataframe(df_res, use_container_width=True)
    with c2:
        fig = px.pie(df_res, values='Valor Atual (€)', names='Ativo', title='Distribuição Atual', hole=0.4)
        st.plotly_chart(fig)
        
else:
    st.info("O portfólio está vazio. Utiliza o painel de execução para adicionar os teus primeiros ativos.")
