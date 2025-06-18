import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata

# Configuração da página
st.set_page_config(page_title="Dashboard Imobiliário", layout="wide")
st.title("🏠 Análise do Impacto da Renda Média Regional no Preço de Imóveis")

# Função para normalizar nomes de colunas
def normalizar_colunas(df):
    df.columns = [
        unicodedata.normalize('NFKD', col)
        .encode('ASCII', 'ignore')
        .decode('utf-8')
        .strip()
        .lower()
        .replace(" ", "_")
        for col in df.columns
    ]
    return df

# Carregamento dos dados
@st.cache_data
def load_data():
    df = pd.read_csv("Brasile-real-estate-dataset.csv")
    df = normalizar_colunas(df)

    # Conversão da coluna de preço para float
    df["preco_brl"] = (
        df["preco_brl"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .str.replace("R$", "", regex=False)
        .str.replace(" ", "", regex=False)
        .astype(float)
    )

    # Tradução dos tipos de imóvel
    if "tipo_imovel" in df.columns:
        df["tipo_imovel"] = df["tipo_imovel"].replace({
            "apartment": "Apartamento",
            "house": "Casa"
        })

    # Tradução das regiões
    if "regiao" in df.columns:
        df["regiao"] = df["regiao"].replace({
            "north": "Norte",
            "northeast": "Nordeste",
            "central-west": "Centro-Oeste",
            "southeast": "Sudeste",
            "south": "Sul"
        })

    return df

# Carregar dados
df = load_data()

# Exibir dados
st.subheader("🔎 Pré-visualização dos dados")
st.dataframe(df.head())

# Filtros interativos com MULTISELECT e opção "Todos"
estados = sorted(df["estado"].dropna().unique())
estados_opcoes = ["Todos"] + estados
estados_selecionados = st.sidebar.multiselect("Selecione o(s) Estado(s)", estados_opcoes, default=["Todos"])

tipos = sorted(df["tipo_imovel"].dropna().unique())
tipos_opcoes = ["Todos"] + tipos
tipos_selecionados = st.sidebar.multiselect("Selecione o(s) Tipo(s) de Imóvel", tipos_opcoes, default=["Todos"])

# Aplicar filtros
df_filtrado = df.copy()
if "Todos" not in estados_selecionados:
    df_filtrado = df_filtrado[df_filtrado["estado"].isin(estados_selecionados)]

if "Todos" not in tipos_selecionados:
    df_filtrado = df_filtrado[df_filtrado["tipo_imovel"].isin(tipos_selecionados)]

# Gráfico 1 - Preço médio por região e tipo de imóvel (filtrado por estado e tipo)
st.subheader("💰 Preço Médio por Região")
st.caption(f"Estados: {', '.join(estados_selecionados)} | Tipo(s): {', '.join(tipos_selecionados)}")

colunas_necessarias = {"regiao", "preco_brl"}
if colunas_necessarias.issubset(df_filtrado.columns) and not df_filtrado.empty:
    preco_regiao = (
        df_filtrado.groupby("regiao")["preco_brl"]
        .mean()
        .reset_index()
    )
    fig1 = px.bar(
        preco_regiao,
        x="regiao",
        y="preco_brl",
        color="regiao",
        labels={
            "regiao": "Região",
            "preco_brl": "Preço Médio (R$)"
        },
        title="Preço Médio por Região",
        text_auto=".2s"
    )
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.warning("⚠️ Dados insuficientes para exibir o gráfico com os filtros selecionados.")

# Gráfico 2 - Preço médio por estado
st.subheader("📊 Preço médio por Estado")

if "preco_brl" in df.columns and "estado" in df.columns:
    preco_medio_estado = (
        df.groupby("estado")["preco_brl"]
        .mean()
        .sort_values()
        .reset_index()
    )
    fig2 = px.bar(
        preco_medio_estado,
        x="preco_brl",
        y="estado",
        orientation="h",
        labels={"preco_brl": "Preço Médio (R$)", "estado": "Estado"},
        title="Preço médio dos imóveis por Estado",
        text_auto=".2s"
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.error("⚠️ As colunas 'preco_brl' ou 'estado' não estão disponíveis no DataFrame.")
