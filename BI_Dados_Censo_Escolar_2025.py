import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px


#import plotly.express as px
""" df = px.data.carshare ( ),
fig = px.scatter_map ( df , lat = " latitude " ,
lon = " longitude " ,
color = " peak_hour " ,
size = " car_hours " ,
color_continuous_scale = px.colors.cyclical.IceFire ,
size_max = 15 , zoom = 10 ),
fig.show () """

# ======================
# CARREGAR DADOS
# ======================

escola = pd.read_csv("Tabela_Escola_2025.csv", sep=";", encoding="latin1", low_memory=False)
mat = pd.read_csv("Tabela_Matricula_2025.csv", sep=";", encoding="latin1", low_memory=False)

# ======================
# FILTRAR RR ESTADUAL
# ======================

escola_rr = escola[
    (escola["SG_UF"]=="RR") &
    (escola["TP_DEPENDENCIA"].isin([2,3])) &
    (escola["TP_SITUACAO_FUNCIONAMENTO"]==1)
]

dados = escola_rr.merge(mat, on="CO_ENTIDADE", how="left")

def rede(x):

    if x == 2:
        return "Estadual"
    if x == 3:
        return "Municipal"

dados["REDE"] = dados["TP_DEPENDENCIA"].apply(rede)

# ======================
# LOCALIZAÇÃO
# ======================

def loc(row):

    if row["TP_LOCALIZACAO_DIFERENCIADA"] == 2:
        return "Indígena"

    if row["TP_LOCALIZACAO"] == 1:
        return "Urbana"

    if row["TP_LOCALIZACAO"] == 2:
        return "Rural"

    return "Outros"

dados["LOCALIZACAO"] = dados.apply(loc, axis=1)

# ======================
# ETAPAS
# ======================

dados["AI"] = dados["QT_MAT_FUND_AI"].fillna(0)
dados["AF"] = dados["QT_MAT_FUND_AF"].fillna(0)
dados["EM"] = dados["QT_MAT_MED"].fillna(0)
dados["EJA"] = dados["QT_MAT_EJA"].fillna(0)
dados["TOTAL ESCOLAS"] = dados["CO_ENTIDADE"].fillna(0)

# ======================
# AGRUPAR ESCOLAS
# ======================

escolas = dados.groupby([
    "CO_ENTIDADE",
    "NO_ENTIDADE",
    "NO_MUNICIPIO",
    "REDE",
    "LOCALIZACAO",
    "LATITUDE",
    "LONGITUDE"
])[["AI","AF","EM","EJA","TOTAL ESCOLAS"]].sum().reset_index()

escolas["TOTAL"] = escolas["AI"] + escolas["AF"] + escolas["EM"] + escolas["EJA"]

# ======================
# INDICADORES
# ======================

total_ai = int(escolas["AI"].sum())
total_af = int(escolas["AF"].sum())
total_em = int(escolas["EM"].sum())
total_eja = int(escolas["EJA"].sum())
total_geral = int(escolas["TOTAL"].sum())





# ======================
# GRAFICO ETAPAS
# ======================

etapas = pd.DataFrame({
    "Etapa":["Anos Iniciais","Anos Finais","Ensino Médio","EJA"],
    "Matriculas":[total_ai,total_af,total_em,total_eja],
   
})

graf_etapas = px.pie(
    etapas,
    values="Matriculas",
    names="Etapa",
    title="Matrículas por Etapa",
       
)

graf_etapas.update_layout(
    title_font=dict(
        color="#7ED957",
        size=24
    )
)

# ======================
# APP
# ======================

app = dash.Dash(__name__)

municipios = sorted(escolas["NO_MUNICIPIO"].dropna().unique())

app.layout = html.Div([

    #html.H1("Dashboard Educacional – Rede Estadual RR"),

    html.Label("Rede"),

dcc.Dropdown(
    id="filtro_rede",
    options=[
        {"label":"Todas","value":"Todas"},
        {"label":"Estadual","value":"Estadual"},
        {"label":"Municipal","value":"Municipal"}
    ],
    value="Todas"
),

    html.Div([

    html.Img(
        src="/assets/CENSO_ESCOLAR_2026.png",
        style={"height":"120px"}
    ),

    html.H1(
        "Dashboard Educacional – Rede Estadual de Roraima",
        style={
        "textAlign": "center",
        "color": "#7ED957",
        "fontWeight": "bold"
    },
        
    )

],
style={
    "display":"flex",
    "alignItems":"center",
    "justifyContent":"center"
}),


    # CARDS
    html.Div([
    
        html.Div([
            html.H4("Total Matrículas"),
            html.H2(id="card_total")
        ], className="card card-total"),

        html.Div([
            html.H4("Total de Escolas"),
            html.H2(id="card_escolas")
        ], className="card card-escolas"),

        html.Div([
            html.H4("Anos Iniciais"),
            html.H2(id="card_ai")
        ], className="card card-ai"),

        html.Div([
            html.H4("Anos Finais"),
            html.H2(id="card_af")
        ], className="card card-af"),

        html.Div([
            html.H4("Ensino Médio"),
            html.H2(id="card_em")
        ], className="card card-em"),

        html.Div([
            html.H4("EJA"),
            html.H2(id="card_eja")
        ], className="card card-eja"),

    ], className="cards-container"),

html.Br(),

    # FILTROS

    html.Label("Localização"),

    dcc.Dropdown(
        id="filtro_local",
        options=[
            {"label":"Todas","value":"Todas"},
            {"label":"Urbana","value":"Urbana"},
            {"label":"Rural","value":"Rural"},
            {"label":"Indígena","value":"Indígena"}
        ],
        value="Todas"
    ),

    html.Label("Município"),

    dcc.Dropdown(
        id="filtro_mun",
        options=[{"label":m,"value":m} for m in municipios],
        multi=True
    ),

    # GRÁFICOS

    dcc.Graph(figure=graf_etapas),

    dcc.Graph(id="ranking"),

    dcc.Graph(id="mapa")

])

# ======================
# CALLBACK
# ======================

@app.callback(
    Output("ranking","figure"),
    Output("mapa","figure"),
    Output("card_total","children"),
    Output("card_escolas","children"),
    Output("card_ai","children"),
    Output("card_af","children"),
    Output("card_em","children"),
    Output("card_eja","children"),
    Input("filtro_local","value"),
    Input("filtro_mun","value"),
    Input("filtro_rede","value")
)

def atualizar(local, municipio, rede):

    df = escolas.copy()

    if local != "Todas":
        df = df[df["LOCALIZACAO"] == local]

    if municipio:
        df = df[df["NO_MUNICIPIO"].isin(municipio)]

    if rede != "Todas":
        df = df[df["REDE"] == rede]

        # CALCULAR CARDS
    total_ai = int(df["AI"].sum())
    total_af = int(df["AF"].sum())
    total_em = int(df["EM"].sum())
    total_eja = int(df["EJA"].sum())
    total_geral = int(df["TOTAL"].sum())

    total_escolas = df["CO_ENTIDADE"].nunique()

    ranking = df.sort_values("TOTAL", ascending=False)

    fig_rank = px.bar(
        ranking,
        x="TOTAL",
        y="NO_ENTIDADE",
        orientation="h",
        height=1200,
        title="Ranking de Escolas"
    )

    fig_rank.update_layout(
    title_font=dict(
        color="#7ED957",
        size=24
    ),
#    title_x=0.5
)

    mapa = df.dropna(subset=["LATITUDE","LONGITUDE"])

    fig_mapa = px.scatter_map(
        mapa,
        lat="LATITUDE",
        lon="LONGITUDE",
        size="TOTAL",
        hover_name="NO_ENTIDADE",
        color="LOCALIZACAO",
        zoom=6,
        map_style="open-street-map"
    )

        

    return (
        fig_rank,
        fig_mapa,
        f"{total_geral:,}",
        f"{total_escolas:,}",
        f"{total_ai:,}",
        f"{total_af:,}",
        f"{total_em:,}",
        f"{total_eja:,}"
    )
   
if __name__ == "__main__":
    app.run(debug=True)