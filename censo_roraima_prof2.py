import pandas as pd
import plotly.express as px
import plotly.io as pio

print("Carregando dados...")

# ============================
# 1 CARREGAR BASES
# ============================

escola = pd.read_csv(
    "Tabela_Escola_2025.csv",
    sep=";",
    encoding="latin1",
    low_memory=False
)

mat = pd.read_csv(
    "Tabela_Matricula_2025.csv",
    sep=";",
    encoding="latin1",
    usecols=[
        "CO_ENTIDADE",
        "QT_MAT_FUND_AI",
        "QT_MAT_FUND_AF",
        "QT_MAT_MED",
        "QT_MAT_EJA"
    ]
)

# ============================
# 2 FILTRAR REDE ESTADUAL
# ============================

escola_rr = escola[
    (escola["SG_UF"]=="RR") &
    (escola["TP_DEPENDENCIA"]==2) &
    (escola["TP_SITUACAO_FUNCIONAMENTO"]==1)
]

#dados = escola_rr.merge(mat,on="CO_ENTIDADE",how="left")

dados = mat.merge(
    escola_rr,
    on="CO_ENTIDADE",
    how="inner"
)



# ============================
# 3 CLASSIFICAR LOCALIZAÇÃO
# ============================

def localizar(row):

    if row["TP_LOCALIZACAO_DIFERENCIADA"]==2:
        return "Indígena"

    if row["TP_LOCALIZACAO"]==1:
        return "Urbana"

    if row["TP_LOCALIZACAO"]==2:
        return "Rural"

    return "Outros"

dados["LOCALIZACAO"] = dados.apply(localizar,axis=1)




# ============================
# 4 MATRÍCULAS
# ============================

dados["AI"] = dados["QT_MAT_FUND_AI"].fillna(0)
dados["AF"] = dados["QT_MAT_FUND_AF"].fillna(0)
dados["EM"] = dados["QT_MAT_MED"].fillna(0)
dados["EJA"] = dados["QT_MAT_EJA"].fillna(0)

# ============================
# 5 AGRUPAR ESCOLAS
# ============================




dados["LOCALIZACAO"] = dados["TP_LOCALIZACAO"].map({
1:"Urbana",
2:"Rural",
3:"Indígena"
})


#escolas = dados.groupby([
#    "CO_ENTIDADE",
#    "NO_ENTIDADE",
#    "NO_MUNICIPIO",
#    "LOCALIZACAO"
#])[["AI","AF","EM","EJA"]].sum().reset_index()

escolas = dados.groupby([
"CO_ENTIDADE",
"NO_ENTIDADE",
"NO_MUNICIPIO",
"LOCALIZACAO"
#"LATITUDE",
#"LONGITUDE"
]).agg({
"AI":"sum",
"AF":"sum",
"EM":"sum",
"EJA":"sum"
}).reset_index()


escolas["TOTAL"] = (
    escolas["AI"] +
    escolas["AF"] +
    escolas["EM"] +
    escolas["EJA"]
)

#escolas["ETAPA"] = escolas[["AI","AF","EM","EJA"]].idxmax(axis=1)

escolas["TOTAL"] = escolas[["AI","AF","EM","EJA"]].sum(axis=1)

print("TOTAL MATRÍCULAS:", escolas["TOTAL"].sum())

# ============================
# 6 GEOLOCALIZAÇÃO
# ============================

geo = escola_rr[
    ["CO_ENTIDADE","LATITUDE","LONGITUDE"]
].drop_duplicates()

escolas = escolas.merge(geo,on="CO_ENTIDADE",how="left")

# ============================
# 7 INDICADORES
# ============================

indicadores = escolas.groupby("LOCALIZACAO")[[
    "AI","AF","EM","EJA"
]].sum().reset_index()

fig_indicadores = px.bar(
    indicadores,
    x="LOCALIZACAO",
    y=["AI","AF","EM","EJA"],
    title="Matrículas por Etapa e Localização"
)

# ============================
# 8 RANKING ESCOLAS
# ============================

ranking = escolas.sort_values("TOTAL",ascending=False)

fig_rank = px.bar(
    ranking,
    x="TOTAL",
    y="NO_ENTIDADE",
    orientation="h",
    height=2000,
    title="Ranking de Escolas",
    hover_data=["NO_MUNICIPIO","LOCALIZACAO"]
)





# ============================
# 9 MAPA
# ============================




mapa = escolas.dropna(subset=["LATITUDE","LONGITUDE"])

fig_mapa = px.scatter_map(
    mapa,
    lat="LATITUDE",
    lon="LONGITUDE",
    size="TOTAL",
    color="LOCALIZACAO",
    hover_name="NO_ENTIDADE",
     hover_data=[
        "NO_MUNICIPIO",
        "AI",
        "AF",
        "EM",
        "EJA"
    ],
    animation_frame="NO_MUNICIPIO",
    zoom=6,
    title="Mapa das Escolas Estaduais de Roraima"
)





# ============================
# 10 DIAGNÓSTICO AUTOMÁTICO
# ============================

problemas = []

sem_medio = escolas[escolas["EM"]==0]
problemas.append(f"Escolas sem ensino médio: {len(sem_medio)}")

sem_eja = escolas[escolas["EJA"]==0]
problemas.append(f"Escolas sem EJA: {len(sem_eja)}")

superlotadas = escolas[escolas["TOTAL"]>1000]
problemas.append(f"Escolas com mais de 1000 matrículas: {len(superlotadas)}")

sem_geo = escolas[escolas["LATITUDE"].isna()]
problemas.append(f"Escolas sem geolocalização: {len(sem_geo)}")

diagnostico = "<br>".join(problemas)

# ============================
# 11 GERAR DASHBOARD
# ============================

html = f"""
<html>

<head>
<meta charset="UTF-8">
<title>BI Educacional - Rede Estadual RR</title>

<style>
body {{
font-family: Arial;
margin: 40px;
background-color:#f5f5f5;
}}

h1 {{
color:#003366;
}}

.card {{
background:white;
padding:20px;
margin-bottom:30px;
border-radius:8px;
box-shadow:0px 0px 10px #ccc;
}}
</style>

</head>

<body>

<h1>BI Educacional - Rede Estadual de Roraima</h1>

<div class="card">

<h2>Diagnóstico automático</h2>

<p>{diagnostico}</p>

</div>

<div class="card">

<h2>Indicadores educacionais</h2>

{pio.to_html(fig_indicadores,full_html=False)}

</div>

<div class="card">

<h2>Ranking de escolas</h2>

{pio.to_html(fig_rank,full_html=False)}

</div>

<div class="card">

<h2>Mapa educacional</h2>

{pio.to_html(fig_mapa,full_html=False)}

</div>

</body>

</html>
"""

with open("dados_censo_roraima_prof2.html","w",encoding="utf-8") as f:
    f.write(html)

print("BI educacional criado com sucesso!")

