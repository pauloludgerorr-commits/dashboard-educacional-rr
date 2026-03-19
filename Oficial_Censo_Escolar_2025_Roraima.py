import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from dash import State

from reportlab.platypus import  Spacer
from io import BytesIO

from reportlab.platypus import Table, TableStyle, Image
from reportlab.lib import colors
import plotly.io as pio



# ======================
# TRATAMENTO DE DADOS
# ======================

def carregar_dados():
    escola = pd.read_csv("Tabela_Escola_2025.csv", sep=";", encoding="latin1", low_memory=False)
    mat = pd.read_csv("Tabela_Matricula_2025.csv", sep=";", encoding="latin1", low_memory=False)

    escola_rr = escola[
        (escola["SG_UF"] == "RR") &
        (escola["TP_DEPENDENCIA"].isin([2, 3])) &
        (escola["TP_SITUACAO_FUNCIONAMENTO"] == 1)
    ]

    df = escola_rr.merge(mat, on="CO_ENTIDADE", how="left")

    # REDE
    df["REDE"] = df["TP_DEPENDENCIA"].map({2: "Estadual", 3: "Municipal"})

    # LOCALIZAÇÃO
    def loc(row):
        if row["TP_LOCALIZACAO_DIFERENCIADA"] == 2:
            return "Indígena"
        if row["TP_LOCALIZACAO"] == 1:
            return "Urbana"
        if row["TP_LOCALIZACAO"] == 2:
            return "Rural"
        return "Outros"

    df["LOCALIZACAO"] = df.apply(loc, axis=1)

    # ETAPAS
    df["AI"] = df["QT_MAT_FUND_AI"].fillna(0)
    df["AF"] = df["QT_MAT_FUND_AF"].fillna(0)
    df["EM"] = df["QT_MAT_MED"].fillna(0)
    df["EJA"] = df["QT_MAT_EJA"].fillna(0)

    # 🔥 ESSENCIAL (mapa funcionar)
    df["LATITUDE"] = pd.to_numeric(df["LATITUDE"], errors="coerce")
    df["LONGITUDE"] = pd.to_numeric(df["LONGITUDE"], errors="coerce")

    escolas = df.groupby([
        "CO_ENTIDADE", "NO_ENTIDADE", "NO_MUNICIPIO",
        "REDE", "LOCALIZACAO", "LATITUDE", "LONGITUDE"
    ])[["AI", "AF", "EM", "EJA"]].sum().reset_index()

    escolas["TOTAL"] = escolas[["AI", "AF", "EM", "EJA"]].sum(axis=1)

    return escolas




escolas = carregar_dados()

#municipio_resumo = escolas.groupby("NO_MUNICIPIO")[["AI","AF","EM","EJA","TOTAL"]].sum().reset_index()




#with open("rr_municipios.geojson", "r", encoding="utf-8") as f:
#    geojson = json.load(f)

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

html.Div([


html.Img(
        src="/assets/CENSO_ESCOLAR_2026.png",
        style={"height":"80px"}
    ),

    html.H1(
        "Dashboard Educacional – Roraima",
        style={"marginLeft":"20px"}
    ),
],

style={
    "display":"flex",
    "alignItems":"center",
    "justifyContent":"center",
    "background":"#4c4cd4",
    "color":"white",
    "padding":"15px",
    "borderRadius":"10px"
}),


#    html.H1(
#        "Dashboard Educacional – Rede Estadual de Roraima",
#        style={"textAlign":"center","color":"#7ED957"}
#    ),



dcc.Tabs([

        # ================= DASHBOARD =================
        dcc.Tab(label="📊 Dashboard", children=[

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

            html.Br(),

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

       html.Div([                
        html.P(id="card_variacao")  # 🔥 aqui
], className="card card-total"),

        html.Div([
    html.P(id="card_status")
], className="card card-total"),

        ], className="cards-container"),

       
    html.Br(),

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

            dcc.Graph(figure=graf_etapas),
            dcc.Graph(id="ranking"),
            dcc.Graph(id="mapa"),
            

        ]),

        # ================= INDICADORES =================
        dcc.Tab(label="📈 Indicadores", children=[

            html.H3("Indicadores Educacionais"),
            html.Div([
                dcc.Graph(id="graf_municipio"),
                dcc.Graph(id="graf_etapas_mun"),
                dcc.Graph(id="mapa_municipio"),
                
            ], style={"display":"flex"})
        ]),

        # ================= RELATÓRIO =================
        dcc.Tab(label="📄 Relatório", children=[

            html.H3("Relatório Educacional"),

            html.Label("Municipio"),
dcc.Dropdown(
    id="filtro_municipio",
    options=[{"label":e,"value":e} for e in escolas["NO_MUNICIPIO"].unique()],
    multi=True
),


            html.Label("Escola"),
dcc.Dropdown(
    id="filtro_escola",
    options=[{"label":e,"value":e} for e in escolas["NO_ENTIDADE"].unique()],
    multi=True
),

html.Label("Etapas de Ensino"),
dcc.Dropdown(
    id="filtro_etapa",
    options=[
        {"label":"Anos Iniciais","value":"AI"},
        {"label":"Anos Finais","value":"AF"},
        {"label":"Ensino Médio","value":"EM"},
        {"label":"EJA","value":"EJA"}
    ],
    multi=True
),
            html.Button("Gerar PDF", id="btn_pdf"),


        dcc.Download(id="download_pdf"),

            dash.dash_table.DataTable(
                id="tabela_relatorio",
                columns=[
                    {"name":"Escola","id":"NO_ENTIDADE"},
                    {"name":"Município","id":"NO_MUNICIPIO"},
                    {"name":"Total","id":"TOTAL"},
                ],
                data=escolas.to_dict("records"),
                page_size=20
            )

        ])

    ])

])



# ======================
# CALLBACK
# ======================

def gerar_grafico_imagem(df):
    fig = px.bar(
        df.groupby("NO_MUNICIPIO")["TOTAL"].sum().reset_index(),
        x="NO_MUNICIPIO",
        y="TOTAL",
        title="Matrículas por Município"
    )

    img_bytes = pio.to_image(fig, format="png")
    buffer = BytesIO(img_bytes)
    return buffer



def gerar_pdf_buffer(df):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    conteudo = []

    conteudo.append(Paragraph("Relatório Educacional - Roraima", styles["Title"]))
    conteudo.append(Spacer(1, 10))

   # ================= HEADER =================
    conteudo.append(Paragraph("GOVERNO DO ESTADO DE RORAIMA", styles["Title"]))
    conteudo.append(Paragraph("Secretaria de Educação", styles["Normal"]))
    conteudo.append(Paragraph("Relatório Educacional - Censo Escolar 2025", styles["Heading2"]))
    conteudo.append(Spacer(1, 15))


# ================= INDICADORES =================
    conteudo.append(Paragraph("Resumo Geral", styles["Heading3"]))

    conteudo.append(Paragraph(f"Total de Matrículas: {int(df['TOTAL'].sum()):,}", styles["Normal"]))
    conteudo.append(Paragraph(f"Total de Escolas: {df['CO_ENTIDADE'].nunique()}", styles["Normal"]))
    conteudo.append(Paragraph(f"Municípios: {df['NO_MUNICIPIO'].nunique()}", styles["Normal"]))

    conteudo.append(Spacer(1, 15))

    conteudo.append(Paragraph(f"Anos Iniciais: {int(df['AI'].sum()):,}", styles["Normal"]))
    conteudo.append(Paragraph(f"Anos Finais: {int(df['AF'].sum()):,}", styles["Normal"]))
    conteudo.append(Paragraph(f"Ensino Médio: {int(df['EM'].sum()):,}", styles["Normal"]))
    conteudo.append(Paragraph(f"EJA: {int(df['EJA'].sum()):,}", styles["Normal"]))

    # ================= GRÁFICO =================
    conteudo.append(Paragraph("Gráfico - Matrículas por Município", styles["Heading3"]))

    img_buffer = gerar_grafico_imagem(df)
    img = Image(img_buffer, width=400, height=250)

    conteudo.append(img)
    conteudo.append(Spacer(1, 20))



     # ================= TABELA =================
    conteudo.append(Paragraph("Tabela de Escolas", styles["Heading3"]))

    tabela_dados = [["Escola", "Município", "Total"]]

    for _, row in df.head(20).iterrows():
        tabela_dados.append([
            row["NO_ENTIDADE"],
            row["NO_MUNICIPIO"],
            int(row["TOTAL"])
        ])

    tabela = Table(tabela_dados)

    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.green),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("GRID",(0,0),(-1,-1),1,colors.black),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold")
    ]))

    conteudo.append(tabela)

     # ================= FOOTER =================
    conteudo.append(Spacer(1, 20))
    conteudo.append(Paragraph("Fonte: Censo Escolar 2025 - INEP", styles["Italic"]))

    # ================= BUILD =================
    doc.build(conteudo)

    buffer.seek(0)
    return buffer

    """ conteudo.append(Paragraph(f"Total de Matrículas: {int(df['TOTAL'].sum()):,}", styles["Normal"]))
    conteudo.append(Paragraph(f"Total de Escolas: {df['CO_ENTIDADE'].nunique()}", styles["Normal"]))
    conteudo.append(Paragraph(f"Municípios: {df['NO_MUNICIPIO'].nunique()}", styles["Normal"]))
    conteudo.append(Spacer(1, 10)) """

    """ conteudo.append(Paragraph(f"Anos Iniciais: {int(df['AI'].sum()):,}", styles["Normal"]))
    conteudo.append(Paragraph(f"Anos Finais: {int(df['AF'].sum()):,}", styles["Normal"]))
    conteudo.append(Paragraph(f"Ensino Médio: {int(df['EM'].sum()):,}", styles["Normal"]))
    conteudo.append(Paragraph(f"EJA: {int(df['EJA'].sum()):,}", styles["Normal"]))
 """
    
"""  etapas_map = {
    "AI": "Anos Iniciais",
    "AF": "Anos Finais",
    "EM": "Ensino Médio",
    "EJA": "EJA"
}

    for etapa, nome in etapas_map.items():
        if etapa in df.columns:
            valor = int(df[etapa].sum())
            if valor > 0:
                conteudo.append(Paragraph(f"{nome}: {valor:,}", styles["Normal"]))


                doc.build(conteudo)

            buffer.seek(0)
    return buffer """

@app.callback(
    Output("ranking","figure"),
    Output("mapa","figure"),
    Output("card_total","children"),
    Output("card_escolas","children"),
    Output("card_ai","children"),
    Output("card_af","children"),
    Output("card_em","children"),
    Output("card_eja","children"),
    Output("card_variacao","children"),
    Output("card_status","children"),
    Output("graf_municipio","figure"),
    Output("graf_etapas_mun","figure"),
    Output("mapa_municipio","figure"),

    Input("filtro_local","value"),
    Input("filtro_mun","value"),
    Input("filtro_rede","value"),
    Input("ranking", "clickData"),
)
def atualizar(local, municipio, rede, clickData):

    df = escolas.copy()

    # ================= FILTROS =================
    if local != "Todas":
        df = df[df["LOCALIZACAO"] == local]

    if municipio:
        df = df[df["NO_MUNICIPIO"].isin(municipio)]

    if rede != "Todas":
        df = df[df["REDE"] == rede]

    

    

    # 🔴 proteção
    if df.empty:
        fig = px.bar(title="Sem dados")
        return (
    fig, fig,
    "0","0","0","0","0","0",
    "0%", "Sem dados",
    fig, fig, fig
)
    
    if clickData:
        escola = clickData["points"][0]["y"]
        df = df[df["NO_ENTIDADE"] == escola]

    # ================= CARDS =================
    total_ai = int(df["AI"].sum())
    total_af = int(df["AF"].sum())
    total_em = int(df["EM"].sum())
    total_eja = int(df["EJA"].sum())
    total_geral = int(df["TOTAL"].sum())
    total_escolas = df["CO_ENTIDADE"].nunique()

    media_municipio = df["TOTAL"].mean()

    variacao = ((total_geral - media_municipio) / media_municipio) * 100 if media_municipio > 0 else 0

    if variacao > 0:
            texto = f"{variacao:.1f}% acima da média 🔺"
    else:
            texto = f"{variacao:.1f}% abaixo da média 🔻"




    # 🔥 MÉDIA E VARIAÇÃO
    media_municipio = df["TOTAL"].mean()

    variacao = ((total_geral - media_municipio) / media_municipio) * 100 if media_municipio > 0 else 0

    # ================= RANKING =================
    top10 = df.sort_values("TOTAL", ascending=False).head(10)

    fig_rank = px.bar(
        top10.sort_values("TOTAL"),
        x="TOTAL",
        y="NO_ENTIDADE",
        orientation="h",
        color="TOTAL",
        title="Top 10 Escolas"
    )

    # ================= MAPA =================
    mapa = df.dropna(subset=["LATITUDE","LONGITUDE"])

    if mapa.empty:
        fig_mapa = px.bar(title="Sem coordenadas")
    else:
        fig_mapa = px.scatter_map(
        mapa,
        lat="LATITUDE",
        lon="LONGITUDE",
        size="TOTAL",
        color="TOTAL",
        hover_name="NO_ENTIDADE",
        zoom=6,
        height=600
)

#    fig_mapa.update_traces(
#        marker=dict(size=10)
#)
    
        fig_mapa.update_layout(
        mapbox_style="carto-positron"
)
    
   

    # ================= MUNICÍPIO =================
    mun = df.groupby("NO_MUNICIPIO")["TOTAL"].sum().reset_index()

    fig_municipio = px.bar(
        mun,
        x="NO_MUNICIPIO",
        y="TOTAL",
        color="TOTAL",
        title="Matrículas por Município"
    )

    # ================= ETAPAS =================
    etapas = df.groupby("NO_MUNICIPIO")[["AI","AF","EM","EJA"]].sum().reset_index()

    etapas_melt = etapas.melt(
        id_vars="NO_MUNICIPIO",
        var_name="Etapa",
        value_name="Matriculas"
    )

    fig_etapas = px.bar(
        etapas_melt,
        x="NO_MUNICIPIO",
        y="Matriculas",
        color="Etapa",
        barmode="group"
    )


    media = df["TOTAL"].mean()
    variacao = ((total_geral - media) / media) * 100 if media > 0 else 0

    # ================= MAPA MUNICÍPIO =================
    try:
        with open("rr_municipios.geojson", encoding="utf-8") as f:
            geojson = json.load(f)

        fig_geo = px.choropleth(
            mun,
            geojson=geojson,
            locations="NO_MUNICIPIO",
            featureidkey="properties.nome",
            color="TOTAL"
        )
        fig_geo.update_geos(fitbounds="locations", visible=False)

    except:
        fig_geo = px.bar(title="GeoJSON não encontrado")

    return (
        fig_rank,
        fig_mapa,
        f"{total_geral:,}",
        f"{total_escolas:,}",
        f"{total_ai:,}",
        f"{total_af:,}",
        f"{total_em:,}",
        f"{total_eja:,}",
        f"{variacao:.1f}% vs média",
        texto,
        fig_municipio,
        fig_etapas,
        fig_geo
        
        

    )

   
@app.callback(
    Output("download_pdf", "data"),
    Input("btn_pdf", "n_clicks"),
    State("filtro_local", "value"),
    State("filtro_municipio", "value"),
    State("filtro_rede", "value"),
    State("filtro_escola", "value"),
    State("filtro_etapa", "value"),
    prevent_initial_call=True
)
def gerar_relatorio(n, local, municipio, rede, escola_sel, etapa_sel):

    df = escolas.copy()

    if local != "Todas":
        df = df[df["LOCALIZACAO"] == local]

    if municipio:
        df = df[df["NO_MUNICIPIO"].isin(municipio)]

    if rede != "Todas":
        df = df[df["REDE"] == rede]

    if escola_sel:
        df = df[df["NO_ENTIDADE"].isin(escola_sel)]

    if etapa_sel:
        df["TOTAL"] = df[etapa_sel].sum(axis=1)

    pdf = gerar_pdf_buffer(df)

    return dcc.send_bytes(pdf.read(), "relatorio.pdf") 

   


""" if __name__ == "__main__":
    app.run(debug=True) """


server = app.server

if __name__ == "__main__":
    app.run(debug=True)



