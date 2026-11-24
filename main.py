import os
import httpx

BASE_URL = "https://api.themoviedb.org/3"


def buscar_filme(titulo: str, api_key: str, regiao: str = "BR") -> dict:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json",
    }

    with httpx.Client(base_url=BASE_URL, headers=headers, timeout=8.0) as client:
        busca = client.get(
            "/search/movie",
            params={"query": titulo, "language": "pt-BR", "include_adult": False},
        )
        busca.raise_for_status()
        resultados = busca.json().get("results", [])

        if not resultados:
            return {"erro": f"Nenhum filme encontrado para '{titulo}'."}

        filme_id = resultados[0]["id"]

        detalhes_resp = client.get(
            f"/movie/{filme_id}",
            params={"language": "pt-BR"},
        )
        detalhes_resp.raise_for_status()
        detalhes = detalhes_resp.json()

        provedores_resp = client.get(f"/movie/{filme_id}/watch/providers")
        provedores_resp.raise_for_status()
        dados_regiao = provedores_resp.json().get("results", {}).get(regiao, {})

        streaming = [p["provider_name"] for p in dados_regiao.get("flatrate", [])]
        aluguel = [p["provider_name"] for p in dados_regiao.get("rent", [])]
        compra = [p["provider_name"] for p in dados_regiao.get("buy", [])]

        data_lancamento = detalhes.get("release_date", "")
        ano = data_lancamento.split("-")[0] if data_lancamento else "N/A"

        return {
            "titulo": detalhes.get("title"),
            "ano": ano,
            "generos": [g["name"] for g in detalhes.get("genres", [])],
            "nota": round(detalhes.get("vote_average", 0.0), 1),
            "sinopse": detalhes.get("overview") or "Sinopse não disponível.",
            "disponibilidade": {
                "streaming": streaming,
                "aluguel": aluguel,
                "compra": compra,
            },
        }


if __name__ == "__main__":
    chave = os.getenv("eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2NGI3YjMxYzdmZjRlMGUzNWVhMDBjYTY4MjZkMTliZiIsIm5iZiI6MTc5NTQ4Mzc3NS41MjMsInN1YiI6IjZiMDRlODdmYTRlODQ4ODE2YzBkZDFlZCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.UcohVsh20CdZ_FhFlQlUSiVCKIVWVhKORfdioxGrN00", "")
    if not chave:
        print("Por favor, verifique a sua chave API.")
    else:
        nome = input("Nome do filme: ").strip()
        dados = buscar_filme(nome, chave)
        print(dados)