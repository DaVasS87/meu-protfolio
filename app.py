# --- PERFORMANCE E VISUALIZAÇÃO ---
st.subheader("Performance e Distribuição")
df_hist = pd.read_csv(DATA_FILE)
df_metas = pd.read_csv(META_FILE)

if not df_hist.empty:
    res = []
    for a in df_hist['Ativo'].unique():
        sub = df_hist[df_hist['Ativo'] == a]
        qtd = sub[sub['Tipo']=='Compra']['Qtd'].sum() - sub[sub['Tipo']=='Venda']['Qtd'].sum()
        if qtd > 0:
            preco = yf.Ticker(a).history(period="1d")['Close'].iloc[-1]
            res.append({'Ativo': a, 'Quantidade': round(qtd, 4), 'Valor Atual (€)': round(qtd * preco, 2)})
    
    df_res = pd.DataFrame(res)
    
    # Exibir Tabela e Gráfico
    c1, c2 = st.columns(2)
    with c1:
        st.write("### Posições Reais")
        st.dataframe(df_res, use_container_width=True)
        
    with c2:
        # AQUI É ONDE O GRÁFICO PASSA A USAR AS METAS DA SIDEBAR
        if not df_metas.empty:
            st.write("### Estratégia de Alocação (Target)")
            fig = px.pie(df_metas, values='Percentagem (%)', names='Ativo', title='Distribuição Planeada', hole=0.4)
            st.plotly_chart(fig)
            
        else:
            st.warning("Define as percentagens na sidebar para ver o gráfico de estratégia.")
else:
    st.info("O portfólio está vazio.")
