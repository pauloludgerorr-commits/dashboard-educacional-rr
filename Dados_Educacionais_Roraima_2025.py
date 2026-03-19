import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px

# ======================
# CARREGAR TABELAS
# ======================

escola = pd.read_csv("Tabela_Escola_2025.csv", sep=";", encoding="latin1", low_memory=False)
mat = pd.read_csv("Tabela_Matricula_2025.csv", sep=";", encoding="latin1", low_memory=False)
turma = pd.read_csv("Tabela_Turma_2025.csv", sep=";", encoding="latin1", low_memory=False)
doc = pd.read_csv("Tabela_Docente_2025.csv", sep=";", encoding="latin1", low_memory=False)

# ======================
# UNIFICAR BASE
# ======================

turma = turma[[
"CO_ENTIDADE",
"QT_TUR_BAS"
]]

doc = doc[[
"CO_ENTIDADE",
"QT_DOC_BAS"
]]

#turma_escola = turma.groupby("CO_ENTIDADE")["CO_TURMA"].count().reset_index()
#turma_escola.rename(columns={"CO_TURMA":"TOTAL_TURMAS"}, inplace=True)


#doc_escola = doc.groupby("CO_ENTIDADE")["CO_PESSOA_FISICA"].nunique().reset_index()
#doc_escola.rename(columns={"CO_PESSOA_FISICA":"TOTAL_PROFESSORES"}, inplace=True)



dados = escola.merge(mat, on="CO_ENTIDADE", how="left")
dados = dados.merge(turma, on="CO_ENTIDADE", how="left")
dados = dados.merge(doc, on="CO_ENTIDADE", how="left")

# ======================
# FILTRAR RR ESTADUAL
# ======================

dados = dados[
    (dados["SG_UF"]=="RR") &
    (dados["TP_DEPENDENCIA"]==2) &
    (dados["TP_SITUACAO_FUNCIONAMENTO"]==1)
]

# ======================
# INDICADORES GERAIS
# ======================

total_escolas = dados["CO_ENTIDADE"].nunique()

total_matriculas = dados["QT_MAT_BAS"].sum()

total_turmas = dados["QT_TUR_BAS"].sum()

total_professores = dados["QT_DOC_BAS"].sum()

# ======================
# INDICADORES DE GESTÃO
# ======================

aluno_por_turma = total_matriculas / total_turmas

aluno_por_prof = total_matriculas / total_professores

prof_por_turma = total_professores / total_turmas

# ======================
# LOCALIZAÇÃO
# ======================

def localizacao(row):

    if row["TP_LOCALIZACAO_DIFERENCIADA"] == 2:
        return "Indígena"

    if row["TP_LOCALIZACAO"] == 1:
        return "Urbana"

    if row["TP_LOCALIZACAO"] == 2:
        return "Rural"

    return "Outros"

dados["LOCALIZACAO"] = dados.apply(localizacao, axis=1)

# ======================
# PROFESSORES POR LOCAL
# ======================

prof_local = dados.groupby("LOCALIZACAO")["QT_DOC_BAS"].sum().reset_index()

graf_prof_local = px.bar(
    prof_local,
    x="LOCALIZACAO",
    y="QT_DOC_BAS",
    title="Professores por Localização"
)

# ======================
# TURMAS POR ESCOLA
# ======================

turma_escola = dados.groupby("NO_ENTIDADE")["QT_TUR_BAS"].sum().reset_index()

turma_escola = turma_escola.sort_values("QT_TUR_BAS", ascending=False).head(20)

graf_turmas = px.bar(
    turma_escola,
    x="QT_TUR_BAS",
    y="NO_ENTIDADE",
    orientation="h",
    title="Top 20 Escolas com Mais Turmas"
)

# ======================
# DÉFICIT DE PROFESSORES
# ======================

""" dados["DEFICIT_MAT"] = dados["QT_TUR_BAS_DISC_MATEMATICA" ] - dados["QT_DOC_BAS_DISC_MATEMATICA"]

deficit = dados[["NO_ENTIDADE","DEFICIT_MAT"]]

deficit = deficit.sort_values("DEFICIT_MAT", ascending=False).head(20)

graf_deficit = px.bar(
    deficit,
    x="DEFICIT_MAT",
    y="NO_ENTIDADE",
    orientation="h",
    title="Escolas com Maior Déficit de Professor de Matemática"
) """

# ======================
# DASHBOARD
# ======================

app = dash.Dash(__name__)

app.layout = html.Div([

    html.H1("BI Educacional - Rede Estadual RR"),

    # CARDS
    html.Div([

        html.Div([
            html.H3("Escolas"),
            html.H2(f"{total_escolas:,}")
        ], className="card card-total"),

        html.Div([
            html.H3("Matrículas"),
            html.H2(f"{int(total_matriculas):,}")
        ], className="card card-matriculas"),

        html.Div([
            html.H3("Turmas"),
            html.H2(f"{int(total_turmas):,}")
        ], className="card card-turmas"),

        html.Div([
            html.H3("Professores"),
            html.H2(f"{int(total_professores):,}")
        ], className="card card-professores"),

    ], style={"display":"flex","gap":"20px"}),

    html.Br(),

    html.Div([

        html.Div([
            html.H4("Alunos por Turma"),
            html.H2(f"{aluno_por_turma:.1f}")
        ], className="card card-aluno_por_turma"),

        html.Div([
            html.H4("Alunos por Professor"),
            html.H2(f"{aluno_por_prof:.1f}")
        ], className="card"),

        html.Div([
            html.H4("Professores por Turma"),
            html.H2(f"{prof_por_turma:.2f}")
        ], className="card"),

    ], style={"display":"flex","gap":"20px"}),

    html.Br(),

    dcc.Graph(figure=graf_prof_local),

    dcc.Graph(figure=graf_turmas),

#    dcc.Graph(figure=graf_deficit)

])

if __name__ == "__main__":
    app.run(debug=True)