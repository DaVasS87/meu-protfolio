import streamlit as st
import yfinance as yf
import pandas as pd
import os

# Título da Página
st.title("📊 Meu Portefólio de Investimentos")

# Ficheiro local (no Streamlit Cloud, isto fica na pasta do projeto)
caminho_arquivo = "portfolio_dinamico.csv"

# Carregar dados
if os.path.exists(caminho_arquivo):
    df = pd.read_csv(caminho_arquivo, index_col=0)
else:
    df = pd.DataFrame(columns=['Qtd', 'Preco_Compra'])

# --- Interface ---
st.subheader("Adicionar/Reforçar Investimento")
novos_ativos_input = st.text_input("Ativos (separados por vírgula, ex: TTE.PA, SAN.MC):")
novo_investimento_total = st.number_input("Valor total a investir (€):", min_value=0.0, step=10.0)

if st.button("Processar Compra"):
    if novos_ativos_input and novo_investimento_total > 0:
        novos_ativos = [a.strip() for a in novos_ativos_input.split(',')]
        valor_por_acao = novo_investimento_total / len(novos_ativos)
        
        for ticker in novos_ativos:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            if not hist.empty:
                preco_hoje = hist['Close'].iloc[-1]
                qtd_comprada = valor_por_acao / preco_hoje
                
                if ticker in df.index:
                    investimento_atual = df.loc[ticker, 'Qtd'] * df.loc[ticker, 'Preco_Compra']
                    nova_qtd = df.loc[ticker, 'Qtd'] + qtd_comprada
                    df.loc[ticker, 'Preco_Compra'] = (investimento_atual + valor_por_acao) / nova_qtd
                    df.loc[ticker, 'Qtd'] = nova_qtd
                else:
                    df.loc[ticker] = [qtd_comprada, preco_hoje]
        
        df.to_csv(caminho_arquivo)
        st.success("Compra registada com sucesso!")

# --- Mostrar Tabela ---
st.subheader("Estado Atual")
resultados = []
for ticker in df.index:
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5d")
    if not hist.empty:
        preco_atual = hist['Close'].iloc[-1]
        valor_investido = df.loc[ticker, 'Qtd'] * df.loc[ticker, 'Preco_Compra']
        valor_atual = df.loc[ticker, 'Qtd'] * preco_atual
        resultado = valor_atual - valor_investido
        resultados.append({'Ativo': ticker, 'Qtd': round(df.loc[ticker, 'Qtd'], 4), 'Preço Atual': round(preco_atual, 2), 'Resultado (€)': round(resultado, 2)})

df_final = pd.DataFrame(resultados)
st.dataframe(df_final, use_container_width=True)