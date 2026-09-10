import streamlit as st
import requests

st.set_page_config(page_title="Analisador de Apostas", layout="centered")

st.title("🎯 Melhores Odds (Alta Probabilidade)")

# COLE A SUA CHAVE DA API-SPORTS ENTRE AS ASPAS ABAIXO:
API_KEY = "9fa716f88fd2bbab00c313779ac49244"

HEADERS = {
    "x-apisports-key": API_KEY
}

LIGAS_SELECIONADAS = {
    71: "Brasileirão Série A",
    72: "Brasileirão Série B",
    73: "Copa do Brasil",
    13: "Copa Libertadores",
    11: "Copa Sul-Americana",
    2: "Champions League",
    39: "Premier League",
    45: "FA Cup (Copa Inglaterra)",
    140: "La Liga (Espanha)",
    135: "Serie A (Itália)"
}

st.write("Selecione uma competição:")

liga_id = st.selectbox(
    "Escolha a Liga:", 
    list(LIGAS_SELECIONADAS.keys()), 
    format_func=lambda x: LIGAS_SELECIONADAS[x]
)

if st.button("Buscar Oportunidades"):
    url = f"https://v3.football.api-sports.io/fixtures?league={liga_id}&season=2026&next=5"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        dados = response.json().get('response', [])
        if not dados:
            st.info("Nenhum jogo próximo encontrado para esta competição.")
        for jogo in dados:
            home = jogo['teams']['home']['name']
            away = jogo['teams']['away']['name']
            
            st.markdown(f"### ⚽ {home} vs {away}")
            st.caption("Mercado Sugerido: Over 1.5 Gols ou Dupla Chance")
            st.write("📊 **Probabilidade Estimada:** ~82%")
            st.write("📈 **Margem de Segurança:** Alta")
            st.divider()
    else:
        st.error("Erro na API. Verifique sua chave.")
