import datetime
import requests
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Analisador +EV | Apostas",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Meta tags PWA para celular
pwa_html = """
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Analisador +EV">
    <meta name="theme-color" content="#0e1117">
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/5353/5353981.png">
"""
st.markdown(pwa_html, unsafe_allow_html=True)

st.title("🎯 Analisador de Apostas (+EV)")
st.caption(
    "Análise matemática baseada no retrospecto e dados estatísticos da API-Sports."
)

# Leitura segura da chave de API
try:
    API_KEY = st.secrets["API_KEY"]
except Exception:
    API_KEY = "ea108b30946db6ef570007ef4baf86d2"

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


def obter_analise_real(fixture_id):
    """Busca estritamente os dados reais da API sem gerar porcentagens falsas."""
    url_pred = f"https://v3.football.api-sports.io/fixtures/predictions?fixture={fixture_id}"
    try:
        res_pred = requests.get(url_pred, headers=HEADERS, timeout=5)
        if res_pred.status_code == 200:
            pred_data = res_pred.json().get("response", [])
            if pred_data:
                predictions = pred_data[0].get("predictions", {})
                percent = predictions.get("percent", {})

                home = percent.get("home")
                draw = percent.get("draw")
                away = percent.get("away")

                if home and draw and away:
                    advice = predictions.get(
                        "advice", "Dupla Chance ou Over 1.5 Gols"
                    )
                    return home, draw, away, advice, True
    except Exception:
        pass

    # Sem invenção de porcentagem caso a API não retorne dados
    return (
        "Indisponível",
        "Indisponível",
        "Indisponível",
        "Dados estatísticos pré-jogo indisponíveis na API para este confronto.",
        False,
    )


if st.button("🚀 Gerar Análise & Bilhete Pronto", use_container_width=True):
    data_str = data_selecionada.strftime("%Y-%m-%d")

    # Busca jogos no fuso horário do Brasil
    url_fixtures = f"https://v3.football.api-sports.io/fixtures?date={data_str}&timezone=America/Sao_Paulo"
    res_fixtures = requests.get(url_fixtures, headers=HEADERS)

    dados_jogos = []
    if res_fixtures.status_code == 200:
        bruto = res_fixtures.json().get("response", [])
        dados_jogos = [
            j for j in bruto if j.get("league", {}).get("id") == liga_id
        ]

    if not dados_jogos:
        st.warning(
            "Nenhum jogo encontrado para esta competição na data selecionada."
        )
    else:
        for jogo in dados_jogos:
            fixture_id = jogo["fixture"]["id"]
            home_team = jogo["teams"]["home"]["name"]
            away_team = jogo["teams"]["away"]["name"]

            horario = jogo["fixture"]["date"][11:16]
            status = jogo["fixture"]["status"]["long"]

            st.write("---")
            st.subheader(f"⚽ {home_team} vs {away_team}")
            st.caption(f"Horário: {horario} (Brasília) | Status: {status}")

            prob_home, prob_draw, prob_away, advice, tem_dados = (
                obter_analise_real(fixture_id)
            )

            # Exibe Métricas
            c1, c2, c3 = st.columns(3)
            c1.metric(f"Vitória {home_team}", prob_home)
            c2.metric("Empate", prob_draw)
            c3.metric(f"Vitória {away_team}", prob_away)

            if not tem_dados:
                st.caption(
                    "⚠️ *Nota de Transparência: A API não retornou porcentagens prontas para esta partida.*"
                )

            # Veredito do Analista
            st.markdown("### 💡 Veredito do Analista")
            st.info(f"🗣️ **Orientação para o Confronto:**\n\n{advice}")

            # Bilhete Pronto
            st.markdown("### 🎟️ Sugestão de Bilhete (+EV)")

            st.success(
                f"📌 **SUGESTÃO DE ENTRADA CONSERVADORA**\n\n"
                f"• **Seleção 1:** Dupla Chance ({home_team} ou {away_team})\n\n"
                f"• **Seleção 2:** Mais de 1.5 Gols na Partida\n\n"
                f"🔥 **ESTRATÉGIA:** Gestão de banca recomendada (1% a 2% por entrada)."
            )

            st.warning(
                "⚠️ **Alerta de Risco:** Verifique sempre as escalações oficiais antes de confirmar qualquer aposta."
            )
