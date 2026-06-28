import streamlit as st
import yfinance as yf
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Portefólio Completo", layout="wide")
st.title("📊 Portefólio: Metas e Transações")

# Caminhos dos arquivos
caminho_transacoes = "historico_transacoes.csv"
caminho_metas = "metas_alocacao.csv"

# Garantir arquivos básicos
if not os.path.exists(caminho_transacoes):
    pd.DataFrame(columns=['Data', 'Tipo', 'Ativo', 'Qtd', 'Preco']).to_csv(caminho_transacoes, index=False)
if not os.path.exists(caminho_metas):
    pd.DataFrame(columns=['Ativo', 'Meta']).to_csv(caminho_metas, index=False)

df_hist = pd.read_csv(caminho_transacoes)
df_metas = pd.read_csv(caminho_metas)

# --- Sidebar: Gestão de Metas ---
with st.sidebar:
    st.header("🎯 Metas de Alocação")
    ativo_meta = st.text_input("Ativo para meta:").upper()
    percentagem = st.slider("Percentagem desejada (%):", 0, 100, 10)
    if st.button("Definir Meta"):
        nova_meta = pd.DataFrame({'Ativo': [ativo_meta], 'Meta': [percentagem]})
        df_metas = pd.concat([df_metas[df_metas['Ativo'] != ativo_meta], nova_meta], ignore_index=True)
        df_metas.to_csv(caminho_metas, index=False)
        st.rerun()

# --- Expander: Compras e Vendas ---
with st.expander("➕ Registar Compra ou Venda"):
    col_a, col_b, col_c, col_d = st.columns(4)
    tipo = col_a.selectbox("Tipo:", ["Compra", "Venda"])
    ativo = col_b.text_input("Ativo:").upper()
    qtd = col_c.number_input("Qtd:", min_value=0.0)
    preco = col_d.number_input("Preço:", min_value=0.0)
    
    if st.button("Guardar Transação"):
        nova_linha = pd.DataFrame({'Data': [datetime.now().strftime("%Y-%m-%d")], 'Tipo': [tipo], 'Ativo': [ativo], 'Qtd': [qtd], 'Preco': [preco]})
        df_hist = pd.concat([df_hist, nova_linha], ignore_index=True)
        df_hist.to_csv(caminho_transacoes, index=False)
        st.rerun()

# --- Cálculo e Gráficos ---
if not df_hist.empty:
    ativos = df_hist['Ativo'].unique()
    resultados = []
    
    for a in ativos:
        sub = df_hist[df_hist['Ativo'] == a]
        qtd_total = sub[sub['Tipo']=='Compra']['Qtd'].sum() - sub[sub['Tipo']=='Venda']['Qtd'].sum()
        if qtd_total > 0:
            custo = (sub[sub['Tipo']=='Compra']['Qtd']*sub[sub['Tipo']=='Compra']['Preco']).sum() - \
                    (sub[sub['Tipo']=='Venda']['Qtd']*sub[sub['Tipo']=='Venda']['Preco']).sum()
            preco_atual = yf.Ticker(a).history(period="1d")['Close'].iloc[-1] if not yf.Ticker(a).history(period="1d").empty else 0
            
            meta_val = df_metas[df_metas['Ativo']==a]['Meta'].iloc[0] if a in df_metas['Ativo'].values else 0
            resultados.append({'Ativo': a, 'Qtd': qtd_total, 'Meta (%)': meta_val, 'Valor Atual (€)': round(qtd_total * preco_atual, 2)})

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Performance Atual")
        st.dataframe(pd.DataFrame(resultados), use_container_width=True)
    with col_g2:
        if resultados:
            df_res = pd.DataFrame(resultados)
            fig = px.pie(df_res, values='Meta (%)', names='Ativo', title='Distribuição das Metas de Alocação')
            st.plotly_chart(fig)
            

# --- Backup ---
if st.button("💾 Download Backup Completo"):
    st.download_button("Clique aqui para baixar", data=open(caminho_transacoes, "rb").read(), file_name="backup.csv")
