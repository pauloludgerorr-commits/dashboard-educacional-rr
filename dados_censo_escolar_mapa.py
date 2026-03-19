import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

print("Carregando dados...")

# =========================
# 1 CARREGAR BASES
# =========================

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
    low_memory=False
)

# =========================
# 2 FILTRAR REDE ESTADUAL RR
# =========================

escola_rr = escola[
    (escola["SG_UF"] == "RR") &
    (escola["TP_DEPENDENCIA"] == 2) &
    (escola["TP_SITUACAO_FUNCIONAMENTO"] == 1) 
#    (escola["IN_REGULAR"] == 1) &
#    (escola["IN_EJA"] == 1) &
#    (escola["IN_PROFISSIONALIZANTE"] == 1) &
#    (escola["IN_ESPECIAL_EXCLUSIVA"] == 0)
]


# =========================
# 3 MERGE
# =========================

dados = escola_rr.merge(
    mat,
    on="CO_ENTIDADE",
    how="left"
)

# =========================
# 4 CLASSIFICAR LOCALIZAÇÃO
# =========================

def localizacao(row):

    if row["TP_LOCALIZACAO_DIFERENCIADA"] == 2:
        return "Indígena"

    if row["TP_LOCALIZACAO"] == 1:
        return "Urbana"

    if row["TP_LOCALIZACAO"] == 2:
        return "Rural"

    return "Outros"

dados["LOCALIZACAO"] = dados.apply(localizacao, axis=1)

# =========================
# 5 INDICADORES
# =========================

dados["AI"] = dados["QT_MAT_FUND_AI"].fillna(0)
dados["AF"] = dados["QT_MAT_FUND_AF"].fillna(0)
dados["EM"] = dados["QT_MAT_MED"].fillna(0)
dados["EJA"] = dados["QT_MAT_EJA"].fillna(0)

# =========================
# 6 AGRUPAR POR ESCOLA
# =========================

escolas = dados.groupby([
    "CO_ENTIDADE",
    "NO_ENTIDADE",
    "NO_MUNICIPIO",
    "LATITUDE",
    "LONGITUDE",
    "LOCALIZACAO"
])[["AI","AF","EM","EJA"]].sum().reset_index()

escolas["TOTAL"] = escolas["AI"] + escolas["AF"] + escolas["EM"] + escolas["EJA"]

# =========================
# 7 KPIs
# =========================

total_ai = int(escolas["AI"].sum())
total_af = int(escolas["AF"].sum())
total_em = int(escolas["EM"].sum())
total_eja = int(escolas["EJA"].sum())

total_matriculas = total_ai + total_af + total_em + total_eja
total_escolas = escolas["CO_ENTIDADE"].nunique()

# =========================
# 8 MATRÍCULAS POR LOCALIZAÇÃO
# =========================

loc = escolas.groupby("LOCALIZACAO")[["AI","AF","EM", "EJA"]].sum().reset_index()

graf_local = px.bar(
    loc,
    x="LOCALIZACAO",
    y=["AI","AF","EM","EJA"],
    barmode="group",
    title="Matrículas por Localização"
)




# =========================
# 9 DISTRIBUIÇÃO POR ETAPA
# =========================

etapas = pd.DataFrame({
"Etapa":["Anos Iniciais","Anos Finais","Ensino Médio", "Eja"],
"Matrículas":[total_ai,total_af,total_em, total_eja]
})

graf_etapas = px.pie(
    etapas,
    names="Etapa",
    values="Matrículas",
    title="Distribuição das Matrículas"
)

# =========================
# 10 RANKING COMPLETO
# =========================

ranking = escolas.sort_values("TOTAL", ascending=False)


graf_rank = px.bar(
    ranking,
    x="TOTAL",
    y="NO_ENTIDADE",
    orientation="h",
    title="Ranking Completo das Escolas por Matrículas",
    height=2000
)

fig_rank = go.Figure()

# Urbana
urbana = ranking[ranking["LOCALIZACAO"]=="Urbana"]

fig_rank.add_trace(
    go.Bar(
        x=urbana["TOTAL"],
        y=urbana["NO_ENTIDADE"],
        orientation="h",
        name="Urbana",
        visible=True
    )
)

# Rural
rural = ranking[ranking["LOCALIZACAO"]=="Rural"]

fig_rank.add_trace(
    go.Bar(
        x=rural["TOTAL"],
        y=rural["NO_ENTIDADE"],
        orientation="h",
        name="Rural",
        visible=False
    )
)

# Indígena
indigena = ranking[ranking["LOCALIZACAO"]=="Indígena"]

fig_rank.add_trace(
    go.Bar(
        x=indigena["TOTAL"],
        y=indigena["NO_ENTIDADE"],
        orientation="h",
        name="Indígena",
        visible=False
    )
)

fig_rank.update_layout(

    title="Ranking de Escolas por Matrículas",

    height=2000,

    updatemenus=[
        dict(
            buttons=list([

                dict(
                    label="Urbana",
                    method="update",
                    args=[{"visible":[True, False, False]}]
                ),

                dict(
                    label="Rural",
                    method="update",
                    args=[{"visible":[False, True, False]}]
                ),

                dict(
                    label="Indígena",
                    method="update",
                    args=[{"visible":[False, False, True]}]
                ),

                dict(
                    label="Todas",
                    method="update",
                    args=[{"visible":[True, True, True]}]
                )

            ]),
            direction="down",
            showactive=True
        )
    ]
)



# =========================
# 11 MAPA DAS ESCOLAS
# =========================

mapa = px.scatter_mapbox(
    escolas,
    lat="LATITUDE",
    lon="LONGITUDE",
    size="TOTAL",
    hover_name="NO_ENTIDADE",
    hover_data={
        "NO_MUNICIPIO":True,
        "TOTAL":True
    },
    color="LOCALIZACAO",
    zoom=6,
    title="Mapa das Escolas Estaduais de Roraima"
)

mapa.update_layout(
    mapbox_style="open-street-map"
)

# =========================
# 12 DIAGNÓSTICO
# =========================

problemas = []

if total_em < total_af:
    problemas.append("Possível evasão entre o Ensino Fundamental e Ensino Médio.")

if loc.loc[loc.LOCALIZACAO=="Rural","EM"].sum() == 0:
    problemas.append("Ausência de Ensino Médio em áreas rurais.")

if loc.loc[loc.LOCALIZACAO=="Indígena","EM"].sum() == 0:
    problemas.append("Baixa oferta de Ensino Médio indígena.")

diagnostico = "<br>".join(problemas)

# =========================
# 13 GERAR HTML
# =========================

html = f"""

<html>

<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Dashboard Censo Escolar RR</title>

<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>

<style>

body {{
font-family: Arial;
background:#f4f6f9;
margin:40px;
}}

.kpis {{
display:flex;
gap:20px;
margin-bottom:30px;
}}

.card {{
background:white;
padding:20px;
border-radius:10px;
flex:1;
text-align:center;
box-shadow:0 2px 10px rgba(0,0,0,0.1);
}}

.section {{
background:white;
padding:25px;
margin-bottom:30px;
border-radius:10px;
box-shadow:0 2px 10px rgba(0,0,0,0.1);
}}

</style>

</head>

<body>

<h1>Dashboard Educacional – Rede Estadual de Roraima</h1>

<div class="kpis">

<div class="card">
<h3>Total Matrículas</h3>
<h1>{total_matriculas:,}</h1>
</div>

<div class="card">
<h3>Anos Iniciais</h3>
<h1>{total_ai:,}</h1>
</div>

<div class="card">
<h3>Anos Finais</h3>
<h1>{total_af:,}</h1>
</div>

<div class="card">
<h3>Ensino Médio</h3>
<h1>{total_em:,}</h1>
</div>

<div class="card">
<h3>EJA</h3>
<h1>{total_eja:,}</h1>
</div>

<div class="card">
<h3>Escolas</h3>
<h1>{total_escolas}</h1>
</div>

</div>

<div class="section">

<h2>Diagnóstico da Rede</h2>

<p>{diagnostico}</p>

</div>

<div class="section">

<h2>Matrículas por Localização</h2>

{graf_local.to_html(full_html=False)}

</div>

<div class="section">

<h2>Distribuição por Etapa</h2>

{graf_etapas.to_html(full_html=False)}

</div>

<div class="section">

<h2>Mapa das Escolas</h2>

{mapa.to_html(full_html=False)}

</div>

<div class="section">

<h2>Ranking Completo das Escolas</h2>

{graf_rank.to_html(full_html=False)}

</div>

</body>

</html>

"""

with open("dados_censo_escolar_roraima_mapa.html","w",encoding="utf-8") as f:
    f.write(html)

print("Dashboard criado com sucesso!")