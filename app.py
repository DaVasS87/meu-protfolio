import streamlit as st
import yfinance as yf
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# Configuração da Página
st.set_page_config(page_title="Gestão de Portfólio", layout="wide")
st.title("📈 App de Gestão de Portfólio")

DATA_FILE = "transacoes.csv"
META_FILE = "alocacao.csv"

# --- FUNÇÃO DE INICIALIZAÇÃO ---
def inicializar_base():
    dados_iniciais = [
        {'Data': datetime.now().strftime("%Y-%m-%d"), 'Tipo': 'Compra', 'Ativo': 'ALV.DE', 'Qtd': 1, 'Preco': 71.16},
        {'Data': datetime.now().strftime("%Y-%m-%d"), 'Tipo': 'Compra', 'Ativo': 'CVX', 'Qtd': 1, 'Preco': 63.33},
        {'Data': datetime.now().strftime("%Y-%m-%d"), 'Tipo': 'Compra', 'Ativo': 'TTE.PA', 'Qtd': 1, 'Preco': 60.45},
        {'Data': datetime.now().strftime("%Y-%m-%d"), 'Tipo': 'Compra', 'Ativo': 'ZURN.SW', 'Qtd': 1, 'Preco': 69.77}
    ]
    pd.DataFrame(dados_iniciais).to_csv(DATA_FILE, index=False)
    pd.DataFrame({'Ativo': ['ALV.DE', 'CVX', 'TTE.PA', 'ZURN.SW'], 'Percentagem (%)': [27, 24, 23, 26]}).to_csv(META_FILE, index=False)

# Verificar e garantir que os ficheiros existem
if not os.path.exists(DATA_FILE) or not os.path.exists(META_FILE):
    inicializar_base()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configurações")
    if st.button("🚨 RESET TOTAL (Estado Inicial)"):
        inicializar_base()
        st.rerun()
    
    st.divider()
    st.subheader("🎯 Definir Estratégia (Target)")
    ativo_alvo = st.selectbox("Ativo:", ["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"])
    pct_alvo = st.slider("Percentagem desejada (%):", 0, 100, 25)
    if st.button("Gravar Estratégia"):
        df_m = pd.read_csv(META_FILE)
        df_m = df_m[df_m['Ativo'] != ativo_alvo]
        nova = pd.DataFrame({'Ativo': [ativo_alvo], 'Percentagem (%)': [pct_alvo]})
        df_m = pd.concat([df_m, nova], ignore_index=True)
        df_m.to_csv(META_FILE, index=False)
        st.rerun()

# --- EXPANDERS ---
with st.expander("➕ Operações em Pack"):
    tipo_op = st.radio("Operação:", ["Compra", "Venda"], horizontal=True)
    valor_total = st.number_input("Montante Total (€):", min_value=0.0, value=500.0)
    ativos_sel = st.multiselect("Seleciona Ativos:", ["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"], default=["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"])
    
    if st.button("Executar Pack"):
        df_h = pd.read_csv(DATA_FILE)
        for ativo in ativos_sel:
            ticker = yf.Ticker(ativo)
            hist = ticker.history(period="1d")
            preco = hist['Close'].iloc[-1] if not hist.empty else 0
            if preco > 0:
                qtd = valor_total / (len(ativos_sel) * preco)
                nova = pd.DataFrame({'Data': [datetime.now().strftime("%Y-%m-%d")], 'Tipo': [tipo_op], 'Ativo': [ativo], 'Qtd': [qtd], 'Preco': [preco]})
                df_h = pd.concat([df_h, nova], ignore_index=True)
        df_h.to_csv(DATA_FILE, index=False)
        st.rerun()

# --- PERFORMANCE ---
st.subheader("Performance e Distribuição")
df_hist = pd.read_csv(DATA_FILE)
df_metas = pd.read_csv(META_FILE)

res = []
for a in df_hist['Ativo'].unique():
    sub = df_hist[df_hist['Ativo'] == a]
    qtd = sub[sub['Tipo']=='Compra']['Qtd'].sum() - sub[sub['Tipo']=='Venda']['Qtd'].sum()
    if qtd > 0:
        ticker = yf.Ticker(a)
        hist = ticker.history(period="1d")
        preco = hist['Close'].iloc[-1] if not hist.empty else 0
        res.append({'Ativo': a, 'Quantidade': round(qtd, 4), 'Valor Atual (€)': round(qtd * preco, 2)})

if len(res) > 0:
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("### Posições Reais")
        st.dataframe(pd.DataFrame(res), use_container_width=True)
    with col_b:
        st.write("### Estratégia (Target)")
else:
    st.info("Portfólio vazio. Usa o pack de operações para começar.")
