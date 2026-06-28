import streamlit as st
import yfinance as yf
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Meu Portefólio", layout="wide")
st.title("📊 Portefólio com Histórico")

caminho_arquivo = "historico_transacoes.csv"

# Carregar histórico (ou criar se não existir)
if os.path.exists(caminho_arquivo):
    df_hist = pd.read_csv(caminho_arquivo)
else:
    df_hist = pd.DataFrame(columns=['Data', 'Tipo', 'Ativo', 'Qtd', 'Preco'])

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
with st.expander("➕ Adicionar Transação"):
    col_a, col_b, col_c = st.columns(3)
    tipo = col_a.selectbox("Tipo:", ["Compra", "Venda"])
    ativo = col_b.text_input("Ativo (ex: TTE.PA):").upper()
    qtd = col_c.number_input("Quantidade:", min_value=0.0)
    preco = st.number_input("Preço unitário:", min_value=0.0)
    
    if st.button("Guardar Transação"):
        nova_linha = pd.DataFrame({'Data': [datetime.now().strftime("%Y-%m-%d")], 'Tipo': [tipo], 'Ativo': [ativo], 'Qtd': [qtd], 'Preco': [preco]})
        df_hist = pd.concat([df_hist, nova_linha], ignore_index=True)
        df_hist.to_csv(caminho_arquivo, index=False)
        st.rerun()

# --- Cálculo de Performance ---
st.subheader("Performance por Ativo")
if not df_hist.empty:
    ativos = df_hist['Ativo'].unique()
    resultados = []
    
    for a in ativos:
        subset = df_hist[df_hist['Ativo'] == a]
        compras = subset[subset['Tipo'] == 'Compra']
        vendas = subset[subset['Tipo'] == 'Venda']
        
        qtd_total = compras['Qtd'].sum() - vendas['Qtd'].sum()
        custo_total = (compras['Qtd'] * compras['Preco']).sum() - (vendas['Qtd'] * vendas['Preco']).sum()
        preco_medio = custo_total / qtd_total if qtd_total > 0 else 0
        
        # Preço atual
        ticker_info = yf.Ticker(a).history(period="1d")
        preco_atual = ticker_info['Close'].iloc[-1] if not ticker_info.empty else preco_medio
        
        valor_atual = qtd_total * preco_atual
        lucro_prejuizo = valor_atual - custo_total
        
        resultados.append({'Ativo': a, 'Qtd': qtd_total, 'Preço Médio': round(preco_medio, 2), 'Resultado (€)': round(lucro_prejuizo, 2)})
    
    st.dataframe(pd.DataFrame(resultados), use_container_width=True)
