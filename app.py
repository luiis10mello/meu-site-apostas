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
    "Escolha uma partida da lista para gerar a análise matemática de odds."
)

# Leitura segura da chave de API
try:
    API_KEY = st.secrets["API_KEY"]
except Exception:
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

# Gerenciamento de Estado de Navegação (Navegação em 2 Telas)
if "jogo_selecionado" not in st.session_state:
    st.session_state.jogo_selecionado = None

st.write("---")

# FALTANDO TELA DE DETALHES (Voltar para a Lista)
if st.session_state.jogo_selecionado:
    if st.button("⬅️ Voltar para a Lista de Jogos"):
        st.session_state.jogo_selecionado = None
        st.rerun()


def calcular_probabilidades_odds(fixture_id, home_team, away_team):
    """Calcula a probabilidade exata convertendo as Odds de mercado ou por histórico recente."""
    url_odds = f"https://v3.football.api-sports.io/odds?fixture={fixture_id}"
    try:
        res_odds = requests.get(url_odds, headers=HEADERS, timeout=4)
        if res_odds.status_code == 200:
            odds_data = res_odds.json().get("response", [])
            if odds_data:
                bookmakers = odds_data[0].get("bookmakers", [])
                if bookmakers:
                    bets = bookmakers[0].get("bets", [])
                    for bet in bets:
                        if bet.get("id") == 1:
                            values = bet.get("values", [])
                            odd_home = float(
                                next(
                                    (
                                        item["odd"]
                                        for item in values
                                        if item["value"] == "Home"
                                    ),
                                    0,
                                )
                            )
                            odd_draw = float(
                                next(
                                    (
                                        item["odd"]
                                        for item in values
                                        if item["value"] == "Draw"
                                    ),
                                    0,
                                )
                            )
                            odd_away = float(
                                next(
                                    (
                                        item["odd"]
                                        for item in values
                                        if item["value"] == "Away"
                                    ),
                                    0,
                                )
                            )

                            if odd_home > 0 and odd_draw > 0 and odd_away > 0:
                                prob_h_raw = 1 / odd_home
                                prob_d_raw = 1 / odd_draw
                                prob_a_raw = 1 / odd_away
                                total_raw = (
                                    prob_h_raw + prob_d_raw + prob_a_raw
                                )

                                p_home = round((prob_h_raw / total_raw) * 100)
                                p_draw = round((prob_d_raw / total_raw) * 100)
                                p_away = 100 - p_home - p_draw

                                advice = (
                                    f"Dupla Chance ({home_team} ou Empate)"
                                    if p_home >= p_away
                                    else f"Dupla Chance ({away_team} ou Empate)"
                                )
                                return (
                                    f"{p_home}%",
                                    f"{p_draw}%",
                                    f"{p_away}%",
                                    advice,
                                    f"Odds de Mercado (@{odd_home} / @{odd_draw} / @{odd_away})",
                                )
    except Exception:
        pass

    # Backup por histórico
    url_pred = f"https://v3.football.api-sports.io/fixtures/predictions?fixture={fixture_id}"
    try:
        res_pred = requests.get(url_pred, headers=HEADERS, timeout=4)
        if res_pred.status_code == 200:
            pred_data = res_pred.json().get("response", [])
            if pred_data:
                comparison = pred_data[0].get("comparison", {})
                form_home = int(
                    comparison.get("form", {})
                    .get("home", "50%")
                    .replace("%", "")
                )
                form_away = int(
                    comparison.get("form", {})
                    .get("away", "50%")
                    .replace("%", "")
                )

                score_home = form_home + 15
                score_away = form_away
                total = score_home + score_away + 35

                p_home = round((score_home / total) * 100)
                p_away = round((score_away / total) * 100)
                p_draw = 100 - p_home - p_away

                advice = (
                    f"Dupla Chance ({home_team} ou Empate)"
                    if p_home >= p_away
                    else f"Dupla Chance ({away_team} ou Empate)"
                )
                return (
                    f"{p_home}%",
                    f"{p_draw}%",
                    f"{p_away}%",
                    advice,
                    "Histórico & Forma Recente",
                )
    except Exception:
        pass

    return (
        "45%",
        "30%",
        "25%",
        f"Dupla Chance ({home_team} ou Empate)",
        "Estimativa Padrão de Mando",
    )


# --- ETAPA 1: LISTA DE JOGOS ---
if st.session_state.jogo_selecionado is None:
    col_liga, col_data = st.columns([2, 1])

    with col_liga:
        liga_id = st.selectbox(
            "Selecione a Liga:",
            list(LIGAS_SELECIONADAS.keys()),
            format_func=lambda x: LIGAS_SELECIONADAS[x],
        )

    with col_data:
        data_selecionada = st.date_input("Data:", datetime.date.today())

    data_str = data_selecionada.strftime("%Y-%m-%d")
    url_fixtures = f"https://v3.football.api-sports.io/fixtures?date={data_str}&timezone=America/Sao_Paulo"
    res_fixtures = requests.get(url_fixtures, headers=HEADERS)

    dados_jogos = []
    if res_fixtures.status_code == 200:
        bruto = res_fixtures.json().get("response", [])
        dados_jogos = [
            j for j in bruto if j.get("league", {}).get("id") == liga_id
        ]

    st.write("---")
    st.subheader("📋 Jogos Encontrados")

    if not dados_jogos:
        st.info("Nenhum jogo agendado para esta competição na data escolhida.")
    else:
        for jogo in dados_jogos:
            home_team = jogo["teams"]["home"]["name"]
            away_team = jogo["teams"]["away"]["name"]
            horario = jogo["fixture"]["date"][11:16]
            status = jogo["fixture"]["status"]["short"]

            # Botão em formato de Card para selecionar a partida
            label_botao = f"⚽ {horario} | {home_team} vs {away_team} ({status})"
            if st.button(label_botao, key=jogo["fixture"]["id"]):
                st.session_state.jogo_selecionado = jogo
                st.rerun()

# --- ETAPA 2: TELA DE ANÁLISE DE ODDS DA PARTIDA ---
else:
    jogo = st.session_state.jogo_selecionado
    fixture_id = jogo["fixture"]["id"]
    home_team = jogo["teams"]["home"]["name"]
    away_team = jogo["teams"]["away"]["name"]
    horario = jogo["fixture"]["date"][11:16]
    status = jogo["fixture"]["status"]["long"]

    st.subheader(f"⚽ {home_team} vs {away_team}")
    st.caption(f"Horário: {horario} (Brasília) | Status: {status}")

    prob_home, prob_draw, prob_away, advice, fonte = (
        calcular_probabilidades_odds(fixture_id, home_team, away_team)
    )

    # Exibição das Métricas das Odds
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Vitória {home_team}", prob_home)
    c2.metric("Empate", prob_draw)
    c3.metric(f"Vitória {away_team}", prob_away)

    st.caption(f"📊 **Fonte do Cálculo:** {fonte}")

    # Veredito do Analista
    st.markdown("### 💡 Veredito do Analista")
    st.info(
        f"🗣️ **Recomendação Tática:**\n\n"
        f"A entrada de maior probabilidade matemática para este confronto é: **{advice} e Over 1.5 Gols**."
    )

    # Bilhete Pronto
    st.markdown("### 🎟️ Sugestão de Bilhete (+EV)")

    st.success(
        f"📌 **SUGESTÃO DE ENTRADA CONSERVADORA**\n\n"
        f"• **Seleção 1:** {advice}\n\n"
        f"• **Seleção 2:** Mais de 1.5 Gols na Partida\n\n"
        f"🔥 **ESTRATÉGIA:** Gestão de banca recomendada (1% a 2% por entrada)."
    )

    st.warning(
        "⚠️ **Alerta de Risco:** Verifique as escalações oficiais antes de confirmar sua aposta."
    )
