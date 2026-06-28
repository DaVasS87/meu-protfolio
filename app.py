import streamlit as st
import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO E BASE DE DADOS ---
DB = "portfolio_db.csv"

def garantir_db():
    if not os.path.exists(DB):
        df = pd.DataFrame(columns=['Pie', 'Ativo', 'Qtd', 'Preco_Compra'])
        df.to_csv(DB, index=False)

def carregar_dados():
    return pd.read_csv(DB)

def salvar_dados(df):
    df.to_csv(DB, index=False)

# --- LÓGICA DE NEGÓCIO ---
def comprar_ativo(pie, ativo, valor):
    ticker = yf.Ticker(ativo)
    hist = ticker.history(period="1d")
    if hist.empty:
        return False, "Ativo não encontrado."
    
    preco = hist['Close'].iloc[-1]
    qtd = valor / preco
    
    df = carregar_dados()
    nova_linha = pd.DataFrame({
        'Pie': [pie], 
        'Ativo': [ativo], 
        'Qtd': [qtd], 
        'Preco_Compra': [preco]
    })
    df = pd.concat([df, nova_linha], ignore_index=True)
    salvar_dados(df)
    return True, "Sucesso"

# --- INTERFACE ---
st.set_page_config(page_title="Pie Manager Pro", layout="wide")
st.title("📊 Pie Manager - Gestão de Investimentos")
garantir_db()

# Sidebar: Ações
with st.sidebar:
    st.subheader("Configurar Investimento")
    nome_pie = st.text_input("Nome da Pie", "Minha Pie 1")
    modo = st.radio("Modo:", ["Juntar à existente", "Criar nova"])
    ticker = st.text_input("Ticker (Ex: TTE.PA):").upper()
    valor = st.number_input("Valor (€):", min_value=1.0, value=10.0)
    
    if st.button("Executar Operação"):
        if modo == "Criar nova":
            df = carregar_dados()
            df = df[df['Pie'] != nome_pie]
            salvar_dados(df)
        
        sucesso, msg = comprar_ativo(nome_pie, ticker, valor)
        if sucesso:
            st.success("Operação concluída!")
            st.rerun()
        else:
            st.error(msg)

# Visualização Central
df = carregar_dados()
for pie in df['Pie'].unique():
    st.divider()
    st.header(f"Pie: {pie}")
    sub = df[df['Pie'] == pie]
    
    # Cálculos detalhados
    dados_exibicao = []
    for _, row in sub.iterrows():
        p_atual = yf.Ticker(row['Ativo']).history(period="1d")['Close'].iloc[-1]
        investido = row['Qtd'] * row['Preco_Compra']
        atual = row['Qtd'] * p_atual
        dados_exibicao.append({
            'Ativo': row['Ativo'],
            'Qtd': round(row['Qtd'], 4),
            'Preco Médio': round(row['Preco_Compra'], 2),
            'Valor Atual': round(atual, 2),
            'Resultado': round(atual - investido, 2),
            'Var (%)': round(((atual - investido) / investido) * 100, 2)
        })
    
    df_pie = pd.DataFrame(dados_exibicao)
    st.dataframe(df_pie, use_container_width=True)
    
    total_g = df_pie['Resultado'].sum()
    st.metric("Lucro/Perda Total da Pie", f"{total_g:.2f} €", delta=f"{total_g:.2f} €")
st.plotly_chart(fig)
    st.info("Portfólio vazio. Usa o pack de operações para começar.")
