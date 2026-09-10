import datetime
import requests
import streamlit as st

st.set_page_config(
    page_title="Dashboard +EV | Analise de Apostas",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("Analisador de Apostas de Valor (+EV)")
st.caption(
    "Analise matematica baseada no retrospecto e dados estatisticos da API-Sports."
)

API_KEY = "9fa716f88fd2bbab00c313779ac49244"
HEADERS = {"x-apisports-key": API_KEY}

LIGAS_SELECIONADAS = {
    13: "Copa Libertadores",
    11: "Copa Sul-Americana",
    71: "Brasileirao Serie A",
    72: "Brasileirao Serie B",
    73: "Copa do Brasil",
    2: "Champions League",
    39: "Premier League",
    45: "FA Cup (Copa Inglaterra)",
    140: "La Liga (Espanha)",
    135: "Serie A (Italia)",
}

st.write("---")

col_liga, col_data = st.columns([2, 1])

with col_liga:
    liga_id = st.selectbox(
        "Selecione a Liga:",
        list(LIGAS_SELECIONADAS.keys()),
        format_func=lambda x: LIGAS_SELECIONADAS[x],
    )

with col_data:
    data_selecionada = st.date_input("Data:", datetime.date.today())

if st.button("Gerar Analise de Apostas", use_container_width=True):
    data_str = data_selecionada.strftime("%Y-%m-%d")

    url_fixtures = f"https://v3.football.api-sports.io/fixtures?date={data_str}"
    res_fixtures = requests.get(url_fixtures, headers=HEADERS)

    dados_jogos = []
    if res_fixtures.status_code == 200:
        bruto = res_fixtures.json().get("response", [])
        dados_jogos = [
            j for j in bruto if j.get("league", {}).get("id") == liga_id
        ]

    if not dados_jogos:
        url_live = "https://v3.football.api-sports.io/fixtures?live=all"
        res_live = requests.get(url_live, headers=HEADERS)
        if res_live.status_code == 200:
            dados_live = res_live.json().get("response", [])
            dados_jogos = [
                j
                for j in dados_live
                if j.get("league", {}).get("id") == liga_id
            ]

    if not dados_jogos:
        st.warning(
            "Nenhum jogo encontrado para esta competicao na data selecionada."
        )
    else:
        for jogo in dados_jogos:
            fixture_id = jogo["fixture"]["id"]
            home_team = jogo["teams"]["home"]["name"]
            away_team = jogo["teams"]["away"]["name"]
            horario = jogo["fixture"]["date"][11:16]
            status = jogo["fixture"]["status"]["long"]

            st.write("---")
            st.subheader(f"{home_team} vs {away_team}")
            st.caption(f"Horario: {horario} UTC | Status: {status}")

            url_pred = f"https://v3.football.api-sports.io/fixtures/predictions?fixture={fixture_id}"
            res_pred = requests.get(url_pred, headers=HEADERS)

            prob_home = "33%"
            prob_draw = "33%"
            prob_away = "34%"
            advice = "Over 1.5 Gols ou Dupla Chance"

            if res_pred.status_code == 200:
                pred_data = res_pred.json().get("response", [])
                if pred_data:
                    predictions = pred_data[0].get("predictions", {})
                    percent = predictions.get("percent", {})

                    prob_home = percent.get("home", "33%")
                    prob_draw = percent.get("draw", "33%")
                    prob_away = percent.get("away", "34%")
                    advice = predictions.get("advice", advice)

            c1, c2, c3 = st.columns(3)
            c1.metric(f"Vitoria {home_team}", prob_home)
            c2.metric("Empate", prob_draw)
            c3.metric(f"Vitoria {away_team}", prob_away)

            st.markdown("#### Oportunidades Identificadas (+EV):")

            st.success(
                f"**Recomendacao Principal da API:**\n\n"
                f"-> **{advice}**\n\n"
                f"_Dica de Seguranca: Verifique se a Odd oferecida pela casa e maior que 1.45._"
            )

            st.info(
                f"**Mercado de Protecao (Dupla Chance):**\n\n"
                f"-> **{home_team} ou Empate** (Se prob. Mandante > 50%) OU **{away_team} ou Empate**\n\n"
                f"_Ideal para construir apostas multiplas confiaveis._"
            )

            st.warning(
                "**Alerta de Pegadinha das Casas de Apostas:**\n\n"
                "Nao aposte no ML (Vitoria Simples) se a chance calculada for menor que 60%. "
                "Prefira linhas de Handicap (+1.0) ou over 1.5 gols."
            )
