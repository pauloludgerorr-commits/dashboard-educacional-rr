import pandas as pd
import plotly.express as px

# ===============================
# 1. CARREGAR DADOS
# ===============================

escola = pd.read_csv("Tabela_Escola_2025.csv", sep=";", encoding="latin1", low_memory=False)
mat = pd.read_csv("Tabela_Matricula_2025.csv", sep=";", encoding="latin1", low_memory=False)

# ===============================
# 2. FILTRAR REDE ESTADUAL RR
# ===============================

escola_rr = escola[
    (escola["SG_UF"] == "RR") &
    (escola["TP_DEPENDENCIA"] == 2) &
    (escola["TP_SITUACAO_FUNCIONAMENTO"] == 1)
]

# ===============================
# 3. JUNTAR BASES
# ===============================

dados = escola_rr.merge(mat, on="CO_ENTIDADE", how="left")

# ===============================
# 4. CLASSIFICAR LOCALIZAÇÃO
# ===============================

def localizacao(row):

    if row["TP_LOCALIZACAO_DIFERENCIADA"] == 2:
        return "Indígena"

    if row["TP_LOCALIZACAO"] == 1:
        return "Urbana"

    if row["TP_LOCALIZACAO"] == 2:
        return "Rural"

    return "Outros"

dados["LOCALIZACAO"] = dados.apply(localizacao, axis=1)

# ===============================
# 5. INDICADORES EDUCACIONAIS
# ===============================

dados["AI"] = dados["QT_MAT_FUND_AI"].fillna(0)
dados["AF"] = dados["QT_MAT_FUND_AF"].fillna(0)
dados["EM"] = dados["QT_MAT_MED"].fillna(0)
dados["EJA"] = dados["QT_MAT_EJA"].fillna(0)

total_ai = int(dados["AI"].sum())
total_af = int(dados["AF"].sum())
total_em = int(dados["EM"].sum())
total_eja = int(dados["EJA"].sum())

total_matriculas = total_ai + total_af + total_em + total_eja
total_escolas = dados["CO_ENTIDADE"].nunique()

# ===============================
# 6. MATRÍCULAS POR LOCALIZAÇÃO
# ===============================

loc = dados.groupby("LOCALIZACAO")[["AI","AF","EM","EJA"]].sum().reset_index()

graf_local = px.bar(
    loc,
    x="LOCALIZACAO",
    y=["AI","AF","EM","EJA"],
    barmode="group",
    title="Matrículas por Localização da Escola"
)

# ===============================
# 7. DISTRIBUIÇÃO POR ETAPA
# ===============================

etapas = pd.DataFrame({

"Etapa":[
"Anos Iniciais",
"Anos Finais",
"Ensino Médio",
"Eja"
],

"Matrículas":[
total_ai,
total_af,
total_em,
total_eja
]

})

graf_etapas = px.pie(
    etapas,
    names="Etapa",
    values="Matrículas",
    title="Distribuição das Matrículas por Etapa"
)

# ===============================
# 8. MUNICÍPIOS
# ===============================

mun = dados.groupby("NO_MUNICIPIO")[["AI","AF","EM", "EJA"]].sum().reset_index()

mun["TOTAL"] = mun["AI"] + mun["AF"] + mun["EM"] + mun["EJA"]

graf_municipio = px.bar(
    mun.sort_values("TOTAL", ascending=False),
    x="NO_MUNICIPIO",
    y="TOTAL",
    title="Matrículas por Município"
)

# ===============================
# 9. RANKING ESCOLAS
# ===============================

ranking = dados[[
"NO_ENTIDADE",
"AI",
"AF",
"EM",
"EJA"
]]

ranking["TOTAL"] = ranking["AI"] + ranking["AF"] + ranking["EM"] + ranking['EJA']

ranking = ranking.sort_values("TOTAL", ascending=False).head(15)

graf_rank = px.bar(
    ranking,
    x="TOTAL",
    y="NO_ENTIDADE",
    orientation="h",
    title="Top Escolas por Matrícula"
)

# ===============================
# 10. DIAGNÓSTICO
# ===============================

problemas = []

if total_em < total_af:
    problemas.append("Possível evasão entre o Fundamental e o Ensino Médio.")

if loc.loc[loc.LOCALIZACAO=="Rural","EM"].sum() == 0:
    problemas.append("Ausência de Ensino Médio em escolas rurais.")

if loc.loc[loc.LOCALIZACAO=="Indígena","EM"].sum() == 0:
    problemas.append("Oferta muito baixa de Ensino Médio indígena.")

diagnostico = "<br>".join(problemas)

# ===============================
# 11. GERAR HTML
# ===============================

html = f"""

<html>

<head>

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

<h2>Matrículas por Município</h2>

{graf_municipio.to_html(full_html=False)}

</div>

<div class="section">

<h2>Ranking de Escolas</h2>

{graf_rank.to_html(full_html=False)}

</div>

</body>

</html>

"""

with open("super_dashboard_rr.html","w",encoding="utf-8") as f:
    f.write(html)

print("Dashboard criado com sucesso!")