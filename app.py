import streamlit as st
import yfinance as yf
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Meu Portefólio", layout="wide")
st.title("📊 Portefólio com Metas")

caminho_arquivo = "historico_transacoes.csv"

# Garantir que o ficheiro existe
if not os.path.exists(caminho_arquivo):
    df_inicial = pd.DataFrame(columns=['Data', 'Tipo', 'Ativo', 'Qtd', 'Preco', 'Meta'])
    df_inicial.to_csv(caminho_arquivo, index=False)

df_hist = pd.read_csv(caminho_arquivo)

# --- Gestão de Backup ---
col1, col2 = st.columns(2)
with col1:
    with open(caminho_arquivo, "rb") as file:
        st.download_button("📥 Download Histórico", data=file, file_name="historico.csv", mime="text/csv")
with col2:
    upload = st.file_uploader("📤 Restaurar Histórico", type="csv")
    if upload:
        pd.read_csv(upload).to_csv(caminho_arquivo, index=False)
        st.rerun()

# --- Adicionar Transação ---
with st.expander("➕ Adicionar Operação"):
    col_a, col_b, col_c, col_d = st.columns(4)
    tipo = col_a.selectbox("Tipo:", ["Compra", "Venda"])
    ativo = col_b.text_input("Ativo:").upper()
    qtd = col_c.number_input("Qtd:", min_value=0.0)
    preco = col_d.number_input("Preço unitário (€):", min_value=0.0)
    meta = st.slider("Meta de alocação (%):", 0, 100, 10)
    
    if st.button("Registar"):
        if ativo and qtd > 0:
            nova_linha = pd.DataFrame({
                'Data': [datetime.now().strftime("%Y-%m-%d")], 
                'Tipo': [tipo], 'Ativo': [ativo], 
                'Qtd': [qtd], 'Preco': [preco], 'Meta': [meta]
            })
            df_hist = pd.concat([df_hist, nova_linha], ignore_index=True)
            df_hist.to_csv(caminho_arquivo, index=False)
            st.rerun()

# --- Performance e Metas ---
st.subheader("Estado Atual e Metas")
if not df_hist.empty:
    ativos = df_hist['Ativo'].unique()
    resultados = []
    
    for a in ativos:
        subset = df_hist[df_hist['Ativo'] == a]
        meta_atual = subset['Meta'].iloc[-1] # Pega a última meta definida
        
        compras = subset[subset['Tipo'] == 'Compra']
        vendas = subset[subset['Tipo'] == 'Venda']
        qtd_total = compras['Qtd'].sum() - vendas['Qtd'].sum()
        
        custo_liquido = (compras['Qtd'] * compras['Preco']).sum() - (vendas['Qtd'] * vendas['Preco']).sum()
        
        preco_atual = yf.Ticker(a).history(period="1d")
        p_atual = preco_atual['Close'].iloc[-1] if not preco_atual.empty else (custo_liquido/qtd_total if qtd_total > 0 else 0)
        
        if qtd_total > 0:
            resultados.append({
                'Ativo': a, 
                'Qtd': round(float(qtd_total), 2), 
                'Meta (%)': f"{meta_atual}%",
                'Preço Atual': round(float(p_atual), 2),
                'Resultado (€)': round(float((qtd_total * p_atual) - custo_liquido), 2)
            })
    
    if resultados:
        st.dataframe(pd.DataFrame(resultados), use_container_width=True)
