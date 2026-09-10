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
    "Análise estrita e 100% matemática baseada em Odds e Estatísticas Reais."
)

# Leitura segura da chave de API (compatível com st.secrets)
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

if "jogo_selecionado" not in st.session_state:
    st.session_state.jogo_selecionado = None

st.write("---")

if st.session_state.jogo_selecionado:
    if st.button("⬅️ Voltar para a Lista de Jogos"):
        st.session_state.jogo_selecionado = None
        st.rerun()

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
    
    # Requisição com tratamento de erro visível
    try:
        res_fixtures = requests.get(url_fixtures, headers=HEADERS, timeout=5)
        if res_fixtures.status_code == 200:
            resposta_json = res_fixtures.json()
            bruto = resposta_json.get("response", [])
            dados_jogos = [
                j for j in bruto if j.get("league", {}).get("id") == liga_id
            ]
        else:
            st.error(f"Erro na API (Status {res_fixtures.status_code}): Verifique sua chave de API.")
            dados_jogos = []
    except Exception as e:
        st.error(f"Falha de conexão com a API: {e}")
        dados_jogos = []

    st.write("---")
    st.subheader("📋 Jogos Encontrados")

    if not dados_jogos:
        st.info(f"Nenhum jogo agendado para esta competição na data escolhida ({data_str}). Tente mudar a data ou selecionar o Brasileirão Série A.")
    else:
        for jogo in dados_jogos:
            home_team = jogo["teams"]["home"]["name"]
            away_team = jogo["teams"]["away"]["name"]
            horario = jogo["fixture"]["date"][11:16]
            status = jogo["fixture"]["status"]["short"]

            label_botao = f"⚽ {horario} | {home_team} vs {away_team} ({status})"
            if st.button(label_botao, key=jogo["fixture"]["id"]):
                st.session_state.jogo_selecionado = jogo
                st.rerun()
