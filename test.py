import os
import httpx
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TMDB_READ_TOKEN", "").strip()

if not token:
    print("ERROR: TMDB_READ_TOKEN was not found in .env")
    raise SystemExit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "accept": "application/json",
}

movie_query = input("Enter the movie title: ").strip()
if not movie_query:
    movie_query = "Aftersun"

with httpx.Client(
    base_url="https://api.themoviedb.org/3",
    headers=headers,
    timeout=8.0,
) as client:
    # 1. Search by title
    search_resp = client.get(
        "/search/movie",
        params={"query": movie_query, "language": "en-US", "include_adult": False},
    )
    search_resp.raise_for_status()
    results = search_resp.json().get("results", [])

    if not results:
        print(f"No movie found for '{movie_query}'.")
        raise SystemExit(0)

    movie_id = results[0]["id"]

    # 2. Full movie details (includes genres)
    details_resp = client.get(f"/movie/{movie_id}", params={"language": "en-US"})
    details_resp.raise_for_status()
    details = details_resp.json()

    # 3. Watch providers (region BR)
    providers_resp = client.get(f"/movie/{movie_id}/watch/providers")
    providers_resp.raise_for_status()
    br_data = providers_resp.json().get("results", {}).get("US", {})

    year = (details.get("release_date") or "N/A").split("-")[0]
    genres = [g["name"] for g in details.get("genres", [])]
    rating = round(details.get("vote_average", 0.0), 1)
    overview = details.get("overview") or "Overview not available."

    streaming = [p["provider_name"] for p in br_data.get("flatrate", [])]
    rent = [p["provider_name"] for p in br_data.get("rent", [])]
    buy = [p["provider_name"] for p in br_data.get("buy", [])]

    print("\n--- RESULT ---")
    print("Title:", details.get("title"))
    print("Year:", year)
    print("Genres:", ", ".join(genres) if genres else "N/A")
    print("Rating:", rating)
    print("Overview:", overview)
    print("Streaming:", ", ".join(streaming) if streaming else "None listed")
    print("Rent:", ", ".join(rent) if rent else "None listed")
    print("Buy:", ", ".join(buy) if buy else "None listed")