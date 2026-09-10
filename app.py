def obter_analise_real(fixture_id):
    """Busca estritamente os dados reais da API sem gerar porcentagens falsas."""
    url_pred = f"https://v3.football.api-sports.io/fixtures/predictions?fixture={fixture_id}"
    try:
        res_pred = requests.get(url_pred, headers=HEADERS, timeout=5)
        if res_pred.status_code == 200:
            pred_data = res_pred.json().get("response", [])
            if pred_data:
                percent = pred_data[0].get("predictions", {}).get("percent", {})
                home = percent.get("home")
                draw = percent.get("draw")
                away = percent.get("away")

                if home and draw and away:
                    advice = pred_data[0].get("predictions", {}).get("advice")
                    return home, draw, away, advice, True
    except Exception:
        pass

    # Sem invenção de porcentagem caso a API falhe
    return (
        "Sem Dados",
        "Sem Dados",
        "Sem Dados",
        "Dados estatísticos indisponíveis na API no momento.",
        False,
    )
