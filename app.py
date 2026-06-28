import streamlit as st
import yfinance as yf
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

# 1. Configuração da página
st.set_page_config(page_title="Gestão de Portfólio", layout="wide")
st.title("📈 App de Gestão de Portfólio")

# 2. Definição de ficheiros
DATA_FILE = "transacoes.csv"
META_FILE = "alocacao.csv"

# Garantir persistência
if not os.path.exists(DATA_FILE): 
    pd.DataFrame(columns=['Data', 'Tipo', 'Ativo', 'Qtd', 'Preco']).to_csv(DATA_FILE, index=False)
if not os.path.exists(META_FILE): 
    pd.DataFrame(columns=['Ativo', 'Percentagem (%)']).to_csv(META_FILE, index=False)

# 3. Sidebar: Estratégia
with st.sidebar:
    st.header("⚙️ Configurações")
    st.subheader("🎯 Definir Alocação (Target)")
    ativo_alvo = st.selectbox("Ativo:", ["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"])
    pct_alvo = st.slider("Percentagem desejada (%):", 0, 100, 25)
    if st.button("Gravar Estratégia"):
        df_metas = pd.read_csv(META_FILE)
        df_metas = df_metas[df_metas['Ativo'] != ativo_alvo]
        nova = pd.DataFrame({'Ativo': [ativo_alvo], 'Percentagem (%)': [pct_alvo]})
        pd.concat([df_metas, nova], ignore_index=True).to_csv(META_FILE, index=False)
        st.success("Alocação gravada!")
        st.rerun()

# 4. Expander: Operações
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

# 5. Performance e Gráficos (Lógica centralizada)
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
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("### Posições Reais")
        st.dataframe(df_res, use_container_width=True)
    with col_b:
        if not df_metas.empty:
            st.write("### Estratégia (Target)")
            fig = px.pie(df_metas, values='Percentagem (%)', names='Ativo', hole=0.4)
            st.plotly_chart(fig)
else:
    st.info("Portfólio vazio. Usa o pack de operações para começar.")
