# 📊 Dashboard Educacional – Roraima

> Transformando dados do Censo Escolar em inteligência para tomada de decisão

---

## 🎯 Objetivo

Desenvolver um sistema interativo capaz de analisar e visualizar dados educacionais do estado de Roraima, apoiando gestores públicos na identificação de padrões, desigualdades e oportunidades de melhoria.

---

## 🧠 Problema Resolvido

Bases do Censo Escolar são extensas, complexas e pouco acessíveis para análise rápida.

Este projeto resolve isso ao:

* Consolidar dados em um painel visual
* Permitir filtros dinâmicos por múltiplas dimensões
* Apresentar indicadores estratégicos em tempo real

---

## 🚀 Principais Funcionalidades

* 📍 Mapa interativo das escolas (georreferenciamento)
* 🏫 Ranking das escolas por número de matrículas
* 📊 Indicadores educacionais por etapa:

  * Anos Iniciais (AI)
  * Anos Finais (AF)
  * Ensino Médio (EM)
  * EJA
* 📈 Análise por município
* 🔎 Filtros dinâmicos (rede, localização, município)
* 📄 Geração automática de relatórios em PDF

---

## 📸 Preview do Sistema

> *
><img width="1890" height="938" alt="image" src="https://github.com/user-attachments/assets/68a2e0b0-f7d4-47a6-9aa4-09fe5042a8ef" />
<img width="1894" height="877" alt="image" src="https://github.com/user-attachments/assets/6a0b6761-01a1-4c0a-a07a-9c21a0923817" />

> 
*

![Dashboard Preview](assets/preview.png)

---

## 🛠️ Stack Tecnológica

* Python
* Dash (framework web)
* Plotly (visualização de dados)
* Pandas (tratamento de dados)
* ReportLab (geração de PDF)

---

## 🏗️ Arquitetura do Projeto

```id="p2q3x9"
dashboard/
│
├── app.py                # Aplicação principal
├── requirements.txt      # Dependências
├── Procfile              # Deploy (Render/Heroku)
├── assets/               # Estilos e imagens
├── dados/                # Base de dados (local)
```

---

## ⚙️ Execução Local

```id="8h3v1d"
git clone https://github.com/seu-usuario/dashboard-educacional-rr.git
cd dashboard-educacional-rr
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

---

## 🌐 Deploy

Aplicação pronta para deploy em cloud (Render/Heroku):

```id="q9l2z1"
gunicorn app:server
```

---

## 📊 Insights Gerados

O dashboard permite identificar:

* Concentração de matrículas por município
* Distribuição por etapas de ensino
* Diferenças entre rede estadual e municipal
* Escolas com maior demanda educacional

---

## 📈 Possíveis Expansões

* Integração com banco de dados (PostgreSQL)
* Sistema de login e permissões
* Cadastro manual de dados via interface web
* Indicadores avançados (IDEB, evasão, fluxo escolar)

---

## 👨‍💻 Autor

**Paulo Ludgero**

💼 Focado em dados, automação e análise educacional
📊 Python | Dash | SQL | BI

---

## ⭐ Destaque

Projeto desenvolvido com foco em aplicações reais no setor público, demonstrando capacidade de transformar dados brutos em soluções estratégicas.
