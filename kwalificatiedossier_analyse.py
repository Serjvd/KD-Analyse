import streamlit as st
import tempfile
import os

from pdf_extractor import PDFExtractor
from comparator import DossierComparator
from exporter import ExcelExporter

def extract_data(pdf_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_file.read())
        tmp_path = tmp.name

    extractor = PDFExtractor(tmp_path)
    extractor.extract_text()

    data = {
        "metadata": extractor.extract_metadata(),
        "kerntaken": extractor.extract_kerntaken(),
        "werkprocessen": extractor.extract_werkprocessen(),
        "beroepshouding": extractor.extract_beroepshouding(),
        "context": extractor.extract_context(),
        "resultaat": extractor.extract_resultaat(),
        "vakkennis_vaardigheden": extractor.extract_vakkennis_vaardigheden(),
    }

    os.unlink(tmp_path)
    return data

def analyseer_veranderingen(oud_data, nieuw_data):
    comparator = DossierComparator(oud_data, nieuw_data)
    resultaten = comparator.compare_all()

    # Filter: alleen significante wijzigingen in het nieuwe dossier
    gefilterd = [
        r for r in resultaten
        if (r["impact"] != "Geen wijziging in naam of codering"
            and not (r["codering_oud"] != "-" and r["codering_nieuw"] == "-"))
    ]
    return gefilterd

def main():
    st.set_page_config(page_title="Impactanalyse kwalificatiedossier", layout="wide")
    st.title("🔍 Impactanalyse kwalificatiedossier")
    st.markdown("""
    Upload een oud en nieuw kwalificatiedossier (PDF). 
    Deze applicatie vergelijkt de inhoud en toont welke onderdelen **inhoudelijk zijn gewijzigd of toegevoegd** in het nieuwe dossier.
    """)

    col1, col2 = st.columns(2)
    with col1:
        oud_pdf = st.file_uploader("📂 Oud dossier (PDF)", type="pdf", key="oud")
    with col2:
        nieuw_pdf = st.file_uploader("📂 Nieuw dossier (PDF)", type="pdf", key="nieuw")

    if oud_pdf and nieuw_pdf:
        with st.spinner("Bezig met analyseren van verschillen..."):
            try:
                oud_data = extract_data(oud_pdf)
                nieuw_data = extract_data(nieuw_pdf)

                resultaten = analyseer_veranderingen(oud_data, nieuw_data)

                if resultaten:
                    st.success("✅ Wijzigingen gevonden. Hieronder zie je de impact van het nieuwe dossier.")
                    st.dataframe(resultaten, use_container_width=True)

                    exporter = ExcelExporter(output_dir=".")
                    excel_path = exporter.export_to_excel(resultaten, filename="impactanalyse.xlsx")
                    exporter.format_excel(excel_path)

                    with open(excel_path, "rb") as f:
                        st.download_button(
                            label="📥 Download impactanalyse (Excel)",
                            data=f,
                            file_name="impactanalyse.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.info("Geen significante wijzigingen gevonden.")

            except Exception as e:
                st.error(f"Fout tijdens verwerking: {e}")

    else:
        st.info("Wacht op upload van beide dossiers.")

if __name__ == "__main__":
    main()
