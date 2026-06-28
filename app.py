import streamlit as st
import yfinance as yf
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Portefólio de Energia e Seguros", layout="wide")
st.title("📊 Portefólio: Energia e Seguros")

caminho_transacoes = "historico_transacoes.csv"
caminho_metas = "metas_alocacao.csv"

# Inicialização de ficheiros
if not os.path.exists(caminho_transacoes):
    pd.DataFrame(columns=['Data', 'Tipo', 'Ativo', 'Qtd', 'Preco']).to_csv(caminho_transacoes, index=False)
if not os.path.exists(caminho_metas):
    pd.DataFrame(columns=['Ativo', 'Meta']).to_csv(caminho_metas, index=False)

df_hist = pd.read_csv(caminho_transacoes)
df_metas = pd.read_csv(caminho_metas)

# Sidebar: Definição de Metas
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

# Expander: Compra em Pack
with st.expander("➕ Compra em Pack (Investir capital nos ativos selecionados)"):
    valor_total = st.number_input("Valor total a investir (€):", min_value=0.0, value=500.0)
    ativos_selecionados = st.multiselect("Seleciona os ativos:", ["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"], default=["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"])
    if st.button("Executar Compra em Pack"):
        if ativos_selecionados:
            valor_por_ativo = valor_total / len(ativos_selecionados)
            for ativo in ativos_selecionados:
                ticker = yf.Ticker(ativo)
                hist = ticker.history(period="5d")
                if not hist.empty:
                    preco_atual = hist['Close'].iloc[-1]
                    qtd = valor_por_ativo / preco_atual
                    nova_linha = pd.DataFrame({'Data': [datetime.now().strftime("%Y-%m-%d")], 'Tipo': ['Compra'], 'Ativo': [ativo], 'Qtd': [qtd], 'Preco': [preco_atual]})
                    df_hist = pd.concat([df_hist, nova_linha], ignore_index=True)
            df_hist.to_csv(caminho_transacoes, index=False)
            st.rerun()

# Expander: Registo de Venda
with st.expander("➖ Registar Venda Individual"):
    ativo_venda = st.selectbox("Ativo a vender:", ["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"])
    qtd_venda = st.number_input("Quantidade a vender:", min_value=0.0)
    preco_venda = st.number_input("Preço de venda:", min_value=0.0)
    if st.button("Executar Venda"):
        nova_linha = pd.DataFrame({'Data': [datetime.now().strftime("%Y-%m-%d")], 'Tipo': ['Venda'], 'Ativo': [ativo_venda], 'Qtd': [qtd_venda], 'Preco': [preco_venda]})
        df_hist = pd.concat([df_hist, nova_linha], ignore_index=True)
        df_hist.to_csv(caminho_transacoes, index=False)
        st.rerun()

# Performance e Visualização
st.subheader("Performance Atual")
if not df_hist.empty:
    ativos = df_hist['Ativo'].unique()
    resultados = []
    for a in ativos:
        sub = df_hist[df_hist['Ativo'] == a]
        qtd_total = sub[sub['Tipo']=='Compra']['Qtd'].sum() - sub[sub['Tipo']=='Venda']['Qtd'].sum()
        if qtd_total > 0:
            ticker = yf.Ticker(a)
            hist = ticker.history(period="1d")
            preco_atual = hist['Close'].iloc[-1] if not hist.empty else 0
            meta_val = df_metas[df_metas['Ativo']==a]['Meta'].iloc[0] if a in df_metas['Ativo'].values else 0
            
            item = {'Ativo': a, 'Qtd': round(float(qtd_total), 4), 'Meta (%)': meta_val, 'Valor Atual (€)': round(float(qtd_total * preco_atual), 2)}
            resultados.append(item)

    if len(resultados) > 0:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.dataframe(pd.DataFrame(resultados), use_container_width=True)
        with col_g2:
            fig = px.pie(pd.DataFrame(resultados), values='Meta (%)', names='Ativo', title='Distribuição de Metas', hole=0.3)
            st.plotly_chart(fig)
            
    else:
        st.write("Sem posições ativas no momento.")
else:
    st.info("Regista uma compra para começar.")
