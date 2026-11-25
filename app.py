import streamlit as st
from ai_ocena import analizuj_cv

st.set_page_config(page_title="AI Recruiter", layout="wide")
st.title("AI Recruiter – Analiza i ocena CV")

with st.sidebar:
    st.header("Konfiguracja")
    api_key = st.text_input("Token GitHub Models (ghp_...)", type="password")

col_input1, col_input2 = st.columns(2)
with col_input1:
    wymagania = st.text_area(
        "Wymagania stanowiskowe:",
        height=200,
        placeholder="Np. Python, SQL, 2 lata doświadczenia, wykształcenie wyższe, komunikatywność.",
    )
with col_input2:
    tekst_cv = st.text_area(
        "Treść CV kandydata:",
        height=200,
        placeholder="Wklej treść CV kandydata do analizy...",
    )

if st.button("Oceń kandydata", type="primary"):
    if not api_key or not wymagania.strip() or not tekst_cv.strip():
        st.error("Uzupełnij token API, wymagania oraz treść CV.")
    else:
        with st.spinner("Analizuję CV..."):
            try:
                wynik = analizuj_cv(tekst_cv, wymagania, api_key)

                st.divider()

                # Punkt 5 i 6 MVP: wynik końcowy + kategoryzacja
                kategoria = wynik["kategoria"]
                procent = wynik["wynik_koncowy"]

                if kategoria == "Rekomendowany":
                    st.success(f"### Wynik końcowy: {procent}% — 🟢 {kategoria} (75–100%)")
                elif kategoria == "Częściowy match":
                    st.warning(f"### Wynik końcowy: {procent}% — 🟡 {kategoria} (50–74%)")
                else:
                    st.error(f"### Wynik końcowy: {procent}% — 🔴 {kategoria} (0–49%)")

                # Rozbicie punktacji na 4 kategorie (Punkt 5 MVP)
                st.write("**Punktacja w poszczególnych kategoriach:**")
                cols_wagi = st.columns(4)
                for idx, (nazwa_kat, punkty) in enumerate(wynik["oceny_czastkowe"].items()):
                    cols_wagi[idx].metric(label=nazwa_kat, value=f"{punkty}/100")

                st.divider()

                # Punkt 7 MVP: widok Gap Analysis
                st.subheader("Gap Analysis (Spełnione vs Brakujące wymagania)")
                col_gap1, col_gap2 = st.columns(2)

                with col_gap1:
                    st.success("✅ Spełnione wymagania")
                    if wynik["spelnione_wymagania"]:
                        for item in wynik["spelnione_wymagania"]:
                            st.write(f"- {item}")
                    else:
                        st.write("Brak spełnionych wymagań.")

                with col_gap2:
                    st.warning("❌ Brakujące wymagania")
                    if wynik["brakujace_wymagania"]:
                        for item in wynik["brakujace_wymagania"]:
                            st.write(f"- {item}")
                    else:
                        st.write("Brak brakujących wymagań.")

            except Exception as e:
                st.error(f"Wystąpił błąd: {e}")