import streamlit as st
import yfinance as yf
import pandas as pd
import os
import plotly.express as px # Biblioteca para o gráfico

st.set_page_config(page_title="Gestor de Alocação", layout="wide")
st.title("📊 Gestor de Alocação de Capital")

caminho_arquivo = "alocacao.csv"

# Garantir existência do arquivo
if not os.path.exists(caminho_arquivo):
    df_inicial = pd.DataFrame(columns=['Ativo', 'Percentagem', 'Valor_Alocado'])
    df_inicial.to_csv(caminho_arquivo, index=False)

df = pd.read_csv(caminho_arquivo)

# --- Gestão de Alocação ---
with st.sidebar:
    st.header("Definir Investimento")
    valor_total = st.number_input("Valor total a investir (€):", min_value=0.0, value=500.0)
    
    ativo = st.text_input("Ativo:").upper()
    percentagem = st.slider("Percentagem deste ativo (%):", 0, 100, 10)
    
    if st.button("Adicionar à Distribuição"):
        valor_alocado = (percentagem / 100) * valor_total
        nova_linha = pd.DataFrame({'Ativo': [ativo], 'Percentagem': [percentagem], 'Valor_Alocado': [valor_alocado]})
        df = pd.concat([df, nova_linha], ignore_index=True)
        df.to_csv(caminho_arquivo, index=False)
        st.rerun()

    if st.button("Limpar Tudo"):
        df = pd.DataFrame(columns=['Ativo', 'Percentagem', 'Valor_Alocado'])
        df.to_csv(caminho_arquivo, index=False)
        st.rerun()

# --- Visualização ---
if not df.empty:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Distribuição Atual")
        st.dataframe(df, use_container_width=True)
        
    with col2:
        # Gráfico Pie Chart
        fig = px.pie(df, values='Percentagem', names='Ativo', title='Alocação do Portefólio (%)')
        st.plotly_chart(fig)
        
    st.info(f"Total alocado: {df['Percentagem'].sum()}% | Valor: {df['Valor_Alocado'].sum()}€")
else:
    st.write("Adiciona ativos na barra lateral para começar.")
