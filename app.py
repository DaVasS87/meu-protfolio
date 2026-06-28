import streamlit as st
import yfinance as yf
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Meu Portefólio", layout="wide")
st.title("📊 Portefólio com Histórico")

caminho_arquivo = "historico_transacoes.csv"

# Garantir que o ficheiro existe sempre
if not os.path.exists(caminho_arquivo):
    df_inicial = pd.DataFrame(columns=['Data', 'Tipo', 'Ativo', 'Qtd', 'Preco'])
    df_inicial.to_csv(caminho_arquivo, index=False)

# Carregar histórico
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
with st.expander("➕ Adicionar Transação"):
    col_a, col_b, col_c = st.columns(3)
    tipo = col_a.selectbox("Tipo:", ["Compra", "Venda"])
    ativo = col_b.text_input("Ativo (ex: TTE.PA):").upper()
    qtd = col_c.number_input("Quantidade:", min_value=0.0)
    preco = st.number_input("Preço unitário:", min_value=0.0)
    
    if st.button("Guardar Transação"):
        if ativo and qtd > 0 and preco > 0:
            nova_linha = pd.DataFrame({'Data': [datetime.now().strftime("%Y-%m-%d")], 'Tipo': [tipo], 'Ativo': [ativo], 'Qtd': [qtd], 'Preco': [preco]})
            df_hist = pd.concat([df_hist, nova_linha], ignore_index=True)
            df_hist.to_csv(caminho_arquivo, index=False)
            st.success("Transação guardada!")
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
        
        # Calcular preço médio ponderado
        custo_compras = (compras['Qtd'] * compras['Preco']).sum()
        valor_vendas = (vendas['Qtd'] * vendas['Preco']).sum()
        custo_liquido = custo_compras - valor_vendas
        
        preco_medio = custo_liquido / qtd_total if qtd_total > 0 else 0
        
        # Preço atual do mercado
        ticker_info = yf.Ticker(a).history(period="1d")
        preco_atual = ticker_info['Close'].iloc[-1] if not ticker_info.empty else preco_medio
        
        valor_atual = qtd_total * preco_atual
        lucro_prejuizo = valor_atual - custo_liquido
        
        if qtd_total > 0:
            resultados.append({
                'Ativo': a, 
                'Qtd': round(float(qtd_total), 4), 
                'Preço Médio': round(float(preco_medio), 2), 
                'Preço Atual': round(float(preco_atual), 2),
                'Resultado (€)': round(float(lucro_prejuizo), 2)
            })
    
    if resultados:
        st.dataframe(pd.DataFrame(resultados), use_container_width=True)
    else:
        st.info("Não tens posições abertas no momento.")
else:
    st.info("O teu histórico está vazio. Adiciona a tua primeira transação.")
