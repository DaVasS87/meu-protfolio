import streamlit as st
import yfinance as yf
import pandas as pd
import os

st.set_page_config(page_title="Meu Portefólio", layout="wide")
st.title("📊 Meu Portefólio de Investimentos")

caminho_arquivo = "portfolio_dinamico.csv"

# Carregar dados
if os.path.exists(caminho_arquivo):
    df = pd.read_csv(caminho_arquivo, index_col=0)
else:
    df = pd.DataFrame(columns=['Qtd', 'Preco_Compra'])
    df.to_csv(caminho_arquivo)

# --- Interface de COMPRA ---
with st.expander("➕ Adicionar Compra"):
    novos_ativos_input = st.text_input("Ativos (ex: TTE.PA, SAN.MC):")
    novo_investimento_total = st.number_input("Valor total a investir (€):", min_value=0.0)
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
            st.success("Compra registada! Recarrega a página.")

# --- Interface de VENDA ---
with st.expander("➖ Registar Venda"):
    if not df.empty:
        ativo_a_vender = st.selectbox("Escolhe o ativo a vender:", df.index)
        qtd_a_vender = st.number_input("Quantidade a vender:", min_value=0.0, max_value=float(df.loc[ativo_a_vender, 'Qtd']))
        if st.button("Processar Venda"):
            df.loc[ativo_a_vender, 'Qtd'] -= qtd_a_vender
            if df.loc[ativo_a_vender, 'Qtd'] <= 0:
                df = df.drop(ativo_a_vender)
            df.to_csv(caminho_arquivo)
            st.success("Venda registada! Recarrega a página.")
    else:
        st.write("Não tens ativos para vender.")

# --- Tabela e Gráfico ---
st.subheader("Estado Atual")
if not df.empty:
    resultados = []
    dados_grafico = {}
    for ticker in df.index:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        if not hist.empty:
            preco_atual = hist['Close'].iloc[-1]
            valor_investido = df.loc[ticker, 'Qtd'] * df.loc[ticker, 'Preco_Compra']
            valor_atual = df.loc[ticker, 'Qtd'] * preco_atual
            resultado = valor_atual - valor_investido
            resultados.append({'Ativo': ticker, 'Qtd': round(float(df.loc[ticker, 'Qtd']), 4), 'Preço Atual': round(float(preco_atual), 2), 'Resultado (€)': round(float(resultado), 2)})
            dados_grafico[ticker] = valor_atual

    # Mostrar Tabela
    st.dataframe(pd.DataFrame(resultados), use_container_width=True)
    
    # Mostrar Gráfico
    st.subheader("Distribuição do Portefólio")
    st.pie_chart(pd.Series(dados_grafico))
else:
    st
