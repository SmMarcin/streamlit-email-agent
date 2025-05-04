import streamlit as st
import requests
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader

# Ładowanie zmiennych środowiskowych
load_dotenv()
XAI_API_KEY = os.getenv("XAI_API_KEY")
if not XAI_API_KEY:
    st.error("Brak klucza API w zmiennych środowiskowych.")
    st.stop()

# Funkcja do ekstrakcji tekstu z PDF
def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        st.error(f"Błąd podczas ekstrakcji tekstu z PDF: {str(e)}")
        return None

# Funkcja do generowania maila
def generate_email(meeting_info, user_guidelines, style):
    style_instructions = {
        "civil_engineer_ai": "Profesjonalny, techniczny styl inżyniera budownictwa, precyzyjny i formalny.",
        "child": "Prosty, naiwny styl, jak pismo 6-letniego dziecka, z krótkimi zdaniami i błędami gramatycznymi."
    }
    
    prompt = f"""
    Na podstawie poniższych informacji o spotkaniu:
    {meeting_info}

    Wygeneruj treść maila zgłaszającego udział w spotkaniu, uwzględniając:
    - Wytyczne użytkownika: {user_guidelines}
    - Styl: {style_instructions[style]}
    - Masz zakaz używania ponizszego promptu opisanego jako "Wytyczne uZytkownika" wprost w treści maila. Musisz parafrazować tak wprowadzone Wytyczne.
    - Upewnij się, że mail zawiera anegdotę związaną z budownictwem i AI na końcu.
    """
    
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "grok-3-beta",  # Poprawny model
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 600,  # Zwiększono, aby uwzględnić pełną treść i anegdotę
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            response_json = response.json()
            return response_json.get("choices", [{}])[0].get("message", {}).get("content", "Brak wygenerowanego tekstu")
        else:
            st.error(f"Błąd API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Błąd podczas wywołania API: {str(e)}")
        return None

# Interfejs Streamlit
st.title("Agent do generowania maili zgłoszeniowych")
st.write("Prześlij plik PDF z rozpoznawalnym tekstem, podaj wytyczne i wybierz styl.")

uploaded_file = st.file_uploader("Prześlij plik PDF", type=["pdf"])
guidelines = st.text_area("Podaj wytyczne do maila:")
style = st.selectbox("Wybierz styl maila:", ["Inżynier budownictwa AI", "6-latek"])

if st.button("Generuj mail"):
    try:
        if uploaded_file and guidelines:
            with st.spinner("Przetwarzanie..."):
                meeting_info = extract_text_from_pdf(uploaded_file)
                if meeting_info and meeting_info.strip():
                    style_key = "civil_engineer_ai" if style == "Inżynier budownictwa AI" else "child"
                    email_content = generate_email(meeting_info, guidelines, style_key)
                    if email_content:
                        st.success("Wygenerowano mail:")
                        st.write(email_content)
                    else:
                        st.error("Nie udało się wygenerować maila.")
                else:
                    st.error("Nie udało się wyciągnąć tekstu z PDF.")
        else:
            st.error("Proszę przesłać plik PDF i podać wytyczne.")
    except Exception as e:
        st.error(f"Wystąpił błąd: {str(e)}")

# Informacja o autorze
st.markdown("Strona przygotowana przez Marcina Smolnika jako poglądowy Agent samodzielnie napisany w Python i opublikowany publicznie, bazujący na chatbocie LLM - 2025.04.30")