import streamlit as st
import pandas as pd
import tempfile
import os
from inhoudsanalyse import vergelijk_werkprocessen

def main():
    st.set_page_config(page_title="Kwalificatiedossier Vergelijker", layout="wide")
    st.title("📄 Vergelijk kwalificatiedossiers")

    st.markdown("""
        Upload hieronder een oud en een nieuw kwalificatiedossier in PDF-formaat.
        De applicatie vergelijkt werkprocessen inhoudelijk en genereert een Excelrapport met:
        - codes en namen
        - tekstverschillen
        - impactscore
        - inhoudelijke analyse
    """)

    col1, col2 = st.columns(2)
    with col1:
        oud_pdf = st.file_uploader("⬅️ Oud dossier (PDF)", type="pdf", key="oud")
    with col2:
        nieuw_pdf = st.file_uploader("➡️ Nieuw dossier (PDF)", type="pdf", key="nieuw")

    if oud_pdf and nieuw_pdf:
        with st.spinner("Bezig met analyseren..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp1:
                    tmp1.write(oud_pdf.read())
                    oud_path = tmp1.name

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp2:
                    tmp2.write(nieuw_pdf.read())
                    nieuw_path = tmp2.name

                df = vergelijk_werkprocessen(oud_path, nieuw_path)

                st.success("✅ Analyse voltooid")
                st.dataframe(df)

                excel_path = os.path.join(tempfile.gettempdir(), "vergelijking_resultaat.xlsx")
                df.to_excel(excel_path, index=False)

                with open(excel_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Excelrapport",
                        data=f,
                        file_name="vergelijking_resultaat.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"Er is iets misgegaan: {e}")

if __name__ == "__main__":
    main()
