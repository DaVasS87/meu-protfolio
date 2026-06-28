import streamlit as st
import pandas as pd
import os
import plotly.express as px

st.set_page_config(page_title="Gestor de Alocação Manual", layout="wide")
st.title("🎯 Gestor de Alocação de Capital")

caminho_metas = "alocacao_manual.csv"

# Garantir arquivo
if not os.path.exists(caminho_metas):
    pd.DataFrame(columns=['Ativo', 'Percentagem (%)']).to_csv(caminho_metas, index=False)

df_metas = pd.read_csv(caminho_metas)

# --- Gestão de Alocação ---
with st.sidebar:
    st.header("Configurar Alocação")
    total_capital = st.number_input("Capital Total (€):", min_value=0.0, value=500.0)
    
    ativo = st.selectbox("Ativo:", ["TTE.PA", "ALV.DE", "ZURN.SW", "CVX"])
    pct = st.slider("Percentagem desejada (%):", 0, 100, 25)
    
    if st.button("Aplicar Alocação"):
        df_metas = df_metas[df_metas['Ativo'] != ativo] # Remove se já existir
        nova = pd.DataFrame({'Ativo': [ativo], 'Percentagem (%)': [pct]})
        df_metas = pd.concat([df_metas, nova], ignore_index=True)
        df_metas.to_csv(caminho_metas, index=False)
        st.rerun()
        
    if st.button("Reset Reset"):
        if os.path.exists(caminho_metas):
            os.remove(caminho_metas)
            st.rerun()

# --- Cálculo e Visualização ---
st.subheader("Distribuição do Capital")

if not df_metas.empty:
    df_metas['Valor Alocado (€)'] = (df_metas['Percentagem (%)'] / 100) * total_capital
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.dataframe(df_metas.style.format({'Valor Alocado (€)': '{:.2f}'}), use_container_width=True)
        soma_pct = df_metas['Percentagem (%)'].sum()
        st.metric("Total Percentagem", f"{soma_pct}%", delta=f"{100-soma_pct}% para completar" if soma_pct < 100 else None)
        
    with col2:
        fig = px.pie(df_metas, values='Percentagem (%)', names='Ativo', title='Distribuição de Alocação Desejada', hole=0.3)
        st.plotly_chart(fig)
        
else:
    st.info("Define as percentagens para cada ativo na barra lateral.")
