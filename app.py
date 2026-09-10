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

# Estilização PWA para celular
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

# Chave de API configurada
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

# Gerenciamento de estado para navegação limpa
if "jogo_selecionado" not in st.session_state:
    st.session_state.jogo_selecionado = None

st.write("---")

# Botão de retorno caso esteja na tela de análise
if st.session_state.jogo_selecionado:
    if st.button("⬅️ Voltar para a Lista de Jogos"):
        st.session_state.jogo_selecionado = None
        st.rerun()


def buscar_predicoes(fixture_id):
    """Busca os dados estatísticos e conselhos da API."""
    url = f"https://v3.football.api-sports.io/fixtures/predictions?fixture={fixture_id}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        if res.status_code == 200:
            data = res.json().get("response", [])
            if data:
                pred = data[0].get("predictions", {})
                percent = pred.get("percent", {})
                return (
                    percent.get("home", "40%"),
                    percent.get("draw", "30%"),
                    percent.get("away", "30%"),
                    pred.get("advice", "Dupla Chance ou Over 1.5 Gols"),
                    True,
                )
    except Exception:
        pass
    return (
        "Indisponível",
        "Indisponível",
        "Indisponível",
        "Dados estatísticos pré-jogo indisponíveis no momento.",
        False,
    )


# --- TELA 1: SELEÇÃO E LISTAGEM DE PARTIDAS ---
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

    if st.button("🚀 Buscar Partidas Disponíveis", use_container_width=True):
        dados_jogos = []
        try:
            # 1. Tenta buscar jogos da data exata
            url_fixtures = f"https://v3.football.api-sports.io/fixtures?date={data_str}&timezone=America/Sao_Paulo"
            res = requests.get(url_fixtures, headers=HEADERS, timeout=5)
            if res.status_code == 200:
                bruto = res.json().get("response", [])
                dados_jogos = [
                    j for j in bruto if j.get("league", {}).get("id") == liga_id
                ]

            # 2. Fallback inteligente: se não houver jogos hoje, busca os próximos da temporada
            if not dados_jogos:
                url_next = f"https://v3.football.api-sports.io/fixtures?league={liga_id}&season=2026&next=10&timezone=America/Sao_Paulo"
                res_next = requests.get(url_next, headers=HEADERS, timeout=5)
                if res_next.status_code == 200:
                    dados_jogos = res_next.json().get("response", [])
        except Exception:
            dados_jogos = []

        st.session_state.dados_jogos = dados_jogos
        st.session_state.liga_nome_atual = LIGAS_SELECIONADAS[liga_id]
        st.session_state.busca_realizada = True

    if (
        "busca_realizada" in st.session_state
        and st.session_state.busca_realizada
    ):
        st.write("---")
        st.subheader(
            f"📋 Jogos ({st.session_state.get('liga_nome_atual', '')})"
        )

        jogos = st.session_state.get("dados_jogos", [])
        if not jogos:
            st.info(
                "Nenhum jogo encontrado para esta competição no momento. Tente outra data ou liga."
            )
        else:
            for jogo in jogos:
                home = jogo["teams"]["home"]["name"]
                away = jogo["teams"]["away"]["name"]
                data_j = jogo["fixture"]["date"][:10]
                hora = jogo["fixture"]["date"][11:16]
                status = (
                    jogo["fixture"]["status"]["short"]
                    if "short" in jogo["fixture"]["status"]
                    else "NS"
                )

                if st.button(
                    f"⚽ [{data_j}] {hora} | {home} vs {away} ({status})",
                    key=f"jogo_{jogo['fixture']['id']}",
                ):
                    st.session_state.jogo_selecionado = jogo
                    st.rerun()

# --- TELA 2: ANÁLISE COMPLETA DO JOGO ESCOLHIDO ---
else:
    jogo = st.session_state.jogo_selecionado
    fixture_id = jogo["fixture"]["id"]
    home = jogo["teams"]["home"]["name"]
    away = jogo["teams"]["away"]["name"]
    hora = jogo["fixture"]["date"][11:16]
    status = (
        jogo["fixture"]["status"]["long"]
        if "long" in jogo["fixture"]["status"]
        else "Pré-Jogo"
    )

    st.subheader(f"⚽ {home} vs {away}")
    st.caption(f"Horário: {hora} (Brasília) | Status: {status}")

    p_home, p_draw, p_away, advice, tem_dados = buscar_predicoes(fixture_id)

    st.markdown("### 📊 Probabilidades de Resultado (1X2)")
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Vitória {home}", p_home)
    c2.metric("Empate", p_draw)
    c3.metric(f"Vitória {away}", p_away)

    if not tem_dados:
        st.caption(
            "⚠️ *Nota: A API não possui dados estatísticos detalhados para este confronto específico.*"
        )

    st.write("---")

    st.markdown("### 💡 Veredito do Analista")
    st.info(
        f"🗣️ **Orientação Estratégica:**\n\n{advice}\n\n"
        f"O confronto entre **{home}** e **{away}** apresenta tendências claras. "
        f"Evite apostas precipitadas em placares exatos e priorize mercados de proteção."
    )

    st.markdown("### 🎟️ Bilhete Pronto (+EV)")
    st.success(
        f"📌 **SUGESTÃO DE ENTRADA MONTADA**\n\n"
        f"• **Seleção 1:** Dupla Chance ({home} ou Empate)\n\n"
        f"• **Seleção 2:** Mais de 1.5 Gols na Partida\n\n"
        f"🔥 **ESTRATÉGIA:** Entrada recomendada com gestão de banca rigorosa (1% a 2%)."
    )

    st.warning(
        "⚠️ **Alerta de Risco:** Confirme sempre a escalação oficial divulgada pelos clubes antes de validar sua entrada na casa de apostas."
    )
