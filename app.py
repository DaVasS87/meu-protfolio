import streamlit as st
import yfinance as yf
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# Configuração da Página
st.set_page_config(page_title="Gestão de Portfólio Evolutiva", layout="wide")
st.title("📈 Portfólio: Evolução e Performance")

DATA_FILE = "transacoes.csv"

# --- FUNÇÃO DE INICIALIZAÇÃO ---
def inicializar_base():
    # Estrutura exata com colunas corretas
    dados_iniciais = [
        {'Data': '2026-06-28', 'Tipo': 'Compra', 'Ativo': 'ALV.DE', 'Qtd': 1, 'Preco_Compra': 71.16},
        {'Data': '2026-06-28', 'Tipo': 'Compra', 'Ativo': 'CVX', 'Qtd': 1, 'Preco_Compra': 63.33},
        {'Data': '2026-06-28', 'Tipo': 'Compra', 'Ativo': 'TTE.PA', 'Qtd': 1, 'Preco_Compra': 60.45},
        {'Data': '2026-06-28', 'Tipo': 'Compra', 'Ativo': 'ZURN.SW', 'Qtd': 1, 'Preco_Compra': 69.77}
    ]
    df = pd.DataFrame(dados_iniciais)
    df.to_csv(DATA_FILE, index=False)

# Forçar a criação do ficheiro se não existir ou se faltarem colunas
if not os.path.exists(DATA_FILE):
    inicializar_base()
else:
    # Verificação de segurança: se as colunas não existirem, reset forçado
    df_check = pd.read_csv(DATA_FILE)
    if 'Preco_Compra' not in df_check.columns:
        inicializar_base()

# --- SIDEBAR: OPERAÇÕES ---
with st.sidebar:
    st.header("Operações")
    valor_input = st.number_input("Valor para investir (€):", min_value=0.1, value=10.0)
    ativos_input = st.multiselect("Selecionar ativos:", ["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"])
    
    if st.button("Comprar Agora"):
        if ativos_input:
            valor_por_ativo = valor_input / len(ativos_input)
            df = pd.read_csv(DATA_FILE)
            for ativo in ativos_input:
                preco_atual = yf.Ticker(ativo).history(period="1d")['Close'].iloc[-1]
                qtd = valor_por_ativo / preco_atual
                nova_op = pd.DataFrame({'Data': [datetime.now().strftime("%Y-%m-%d")], 
                                        'Tipo': ['Compra'], 'Ativo': [ativo], 
                                        'Qtd': [qtd], 'Preco_Compra': [preco_atual]})
                df = pd.concat([df, nova_op], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.rerun()
    
    st.divider()
    if st.button("🚨 Reset Total (Apagar tudo)"):
        inicializar_base()
        st.rerun()

# --- CÁLCULO E EVOLUÇÃO ---
df_hist = pd.read_csv(DATA_FILE)
resumo = []

for ativo in df_hist['Ativo'].unique():
    sub = df_hist[df_hist['Ativo'] == ativo]
    qtd_total = sub['Qtd'].sum()
    # Cálculo do preço médio ponderado
    preco_medio = (sub['Qtd'] * sub['Preco_Compra']).sum() / qtd_total
    
    # Preço atual de mercado
    ticker = yf.Ticker(ativo)
    hist = ticker.history(period="1d")
    preco_atual = hist['Close'].iloc[-1] if not hist.empty else preco_medio
    
    valor_investido = qtd_total * preco_medio
    valor_atual = qtd_total * preco_atual
    variacao = valor_atual - valor_investido
    var_pct = (variacao / valor_investido) * 100
    
    resumo.append({
        'Ativo': ativo,
        'Quantidade': round(qtd_total, 3),
        'Valor Investido (€)': round(valor_investido, 2),
        'Valor Atual (€)': round(valor_atual, 2),
        'Resultado (€)': round(variacao, 2),
        'Resultado (%)': f"{round(var_pct, 2)}%"
    })

# --- DISPLAY ---
df_final = pd.DataFrame(resumo)
st.subheader("Performance Atual")
st.dataframe(df_final, use_container_width=True)

# Gráfico
fig = px.bar(df_final, x='Ativo', y='Resultado (€)', color=df_final['Resultado (€)'] >= 0, 
             title="Evolução (Lucro/Prejuízo por Ativo)", 
             color_discrete_map={True: 'green', False: 'red'})
st.plotly_chart(fig)
else:
    st.info("Portfólio vazio. Usa o pack de operações para começar.")
