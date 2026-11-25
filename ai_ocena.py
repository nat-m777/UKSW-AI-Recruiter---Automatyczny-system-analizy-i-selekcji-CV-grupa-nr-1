from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class WynikAnalizyAI(BaseModel):
    hard_skills: int = Field(description="Ocena 0-100 za umiejętności twarde")
    doswiadczenie: int = Field(description="Ocena 0-100 za doświadczenie zawodowe")
    wyksztalcenie: int = Field(description="Ocena 0-100 za wykształcenie")
    soft_skills: int = Field(description="Ocena 0-100 za kompetencje miękkie i dodatkowe")
    spelnione_wymagania: list[str] = Field(description="Lista wymagań ze stanowiska, które kandydat spełnia")
    brakujace_wymagania: list[str] = Field(description="Lista brakujących wymagań (luki kompetencyjne)")


def kategoryzuj_wynik(wynik_koncowy: float) -> str:
    """Punkt 6 MVP"""
    if wynik_koncowy < 50:
        return "Niedopasowany"
    elif wynik_koncowy < 75:
        return "Częściowy match"
    else:
        return "Rekomendowany"


def analizuj_cv(tekst_cv: str, wymagania: str, api_key: str) -> dict:
    """Realizuje punkty 5, 6 i 7 z wymagań MVP z użyciem langchain-openai."""
    llm = ChatOpenAI(
    model="openai/gpt-oss-120b",
    api_key=api_key.strip(),
    base_url="https://api.groq.com/openai/v1",
    temperature=0.1,
)

    structured_llm = llm.with_structured_output(
        WynikAnalizyAI,
        method="function_calling"
    )

    prompt = (
        "Jesteś rekruterem IT. Oceń poniższe CV kandydata względem wymagań stanowiskowych. "
        "Przyznaj punkty od 0 do 100 dla każdej z 4 kategorii oraz wypisz wymagania spełnione i brakujące.\n\n" f"WYMAGANIA STANOWISKOWE:\n{wymagania}\n\n" f"TREŚĆ CV KANDYDATA:\n{tekst_cv}")

    wynik_ai: WynikAnalizyAI = structured_llm.invoke(prompt)

    hard = wynik_ai.hard_skills
    dosw = wynik_ai.doswiadczenie
    wyksz = wynik_ai.wyksztalcenie
    soft = wynik_ai.soft_skills

    # Punkt 5 MVP
    wynik_koncowy = round(hard * 0.40 + dosw * 0.35 + wyksz * 0.15 + soft * 0.10,1,)

    kategoria = kategoryzuj_wynik(wynik_koncowy)

    return {
        "wynik_koncowy": wynik_koncowy,
        "kategoria": kategoria,
        "oceny_czastkowe": {"Hard Skills (40%)": hard,"Doświadczenie (35%)": dosw,"Wykształcenie (15%)": wyksz,"Dodatkowe/Soft Skills (10%)": soft,},
        "spelnione_wymagania": wynik_ai.spelnione_wymagania,
        "brakujace_wymagania": wynik_ai.brakujace_wymagania,
    }