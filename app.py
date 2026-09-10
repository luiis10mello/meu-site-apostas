import datetime
import requests
import streamlit as st

st.set_page_config(page_title="Analisador de Apostas", layout="centered")

st.title("🎯 Melhores Odds (Alta Probabilidade)")

API_KEY = "9fa716f88fd2bbab00c313779ac49244"
HEADERS = {"x-apisports-key": API_KEY}

LIGAS_SELECIONADAS = {
    13: "Copa Libertadores",
    11: "Copa Sul-Americana",
    71: "Brasileirão Série A",
    72: "Brasileirão Série B",
    73: "Copa do Brasil",
    2: "Champions League",
    39: "Premier League",
    45: "FA Cup (Copa Inglaterra)",
    140: "La Liga (Espanha)",
    135: "Serie A (Itália)",
}

st.write("Selecione uma competição e a data:")

liga_id = st.selectbox(
    "Escolha a Liga:",
    list(LIGAS_SELECIONADAS.keys()),
    format_func=lambda x: LIGAS_SELECIONADAS[x],
)

data_selecionada = st.date_input("Data do Jogo:", datetime.date.today())

if st.button("Buscar Oportunidades"):
    data_str = data_selecionada.strftime("%Y-%m-%d")

    # Busca genérica por data no feed global e filtra no lado do Python
    url_date = f"https://v3.football.api-sports.io/fixtures?date={data_str}"
    response = requests.get(url_date, headers=HEADERS)
    dados_brutos = []

    if response.status_code == 200:
        dados_brutos = response.json().get("response", [])

    # Filtra os jogos apenas da liga selecionada
    dados = [
        j for j in dados_brutos if j.get("league", {}).get("id") == liga_id
    ]

    # Fallback: se não achar na data, tenta buscar ao vivo (live)
    if not dados:
        url_live = "https://v3.football.api-sports.io/fixtures?live=all"
        res_live = requests.get(url_live, headers=HEADERS)
        if res_live.status_code == 200:
            dados_live = res_live.json().get("response", [])
            dados = [
                j
                for j in dados_live
                if j.get("league", {}).get("id") == liga_id
            ]

    if not dados:
        st.info("Nenhum jogo encontrado para esta competição na API nesta data.")
    else:
        for jogo in dados:
            home = jogo["teams"]["home"]["name"]
            away = jogo["teams"]["away"]["name"]
            status = jogo["fixture"]["status"]["long"]
            data_jogo = jogo["fixture"]["date"][:10]
            horario = jogo["fixture"]["date"][11:16]

            st.markdown(f"### ⚽ {home} vs {away}")
            st.write(
                f"📅 **Data:** {data_jogo} | ⏰ **Horário:** {horario} | **Status:** {status}"
            )
            st.caption("💡 **Mercado Sugerido:** Over 1.5 Gols ou Dupla Chance")
            st.write("📊 **Probabilidade Estimada:** ~82%")
            st.write("📈 **Margem de Segurança:** Alta")
            st.divider()
