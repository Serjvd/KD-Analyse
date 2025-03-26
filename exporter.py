"""
Module voor het exporteren van vergelijkingsresultaten naar Excel-formaat.
"""
import os
import pandas as pd
from typing import List, Dict, Any, Optional


class ExcelExporter:
    """Klasse voor het exporteren van vergelijkingsresultaten naar Excel-formaat."""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialiseert de ExcelExporter met een output directory.
        
        Args:
            output_dir: Directory waar de Excel-bestanden worden opgeslagen
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export_to_excel(self, 
                        comparison_results: List[Dict[str, Any]], 
                        filename: str = "Vergelijking_kwalificatiedossiers.xlsx") -> str:
        """
        Exporteert vergelijkingsresultaten naar een Excel-bestand.
        
        Args:
            comparison_results: Lijst van dictionaries met vergelijkingsresultaten
            filename: Naam van het Excel-bestand
            
        Returns:
            Pad naar het aangemaakte Excel-bestand
        """
        # Maak een DataFrame van de vergelijkingsresultaten
        df = pd.DataFrame(comparison_results)
        
        # Zorg ervoor dat de kolommen in de juiste volgorde staan
        columns = [
            "codering_oud", "naam_oud", "codering_nieuw", 
            "naam_nieuw", "impact", "pagina"
        ]
        
        # Hernoem kolommen naar gebruiksvriendelijke namen
        column_mapping = {
            "codering_oud": "Codering OUD",
            "naam_oud": "Naam OUD",
            "codering_nieuw": "Codering NIEUW",
            "naam_nieuw": "Naam NIEUW",
            "impact": "Impact op inhoud",
            "pagina": "Pagina"
        }
        
        # Selecteer en hernoem kolommen
        if all(col in df.columns for col in columns):
            df = df[columns].rename(columns=column_mapping)
        
        # Bepaal het volledige pad
        output_path = os.path.join(self.output_dir, filename)
        
        # Exporteer naar Excel
        df.to_excel(output_path, index=False)
        
        # Exporteer ook naar CSV voor extra compatibiliteit
        csv_path = output_path.replace('.xlsx', '.csv')
        df.to_csv(csv_path, index=False, sep=';')
        
        return output_path
    
    def format_excel(self, 
                    excel_path: str, 
                    add_filters: bool = True, 
                    auto_column_width: bool = True) -> str:
        """
        Voegt opmaak toe aan een bestaand Excel-bestand.
        
        Args:
            excel_path: Pad naar het Excel-bestand
            add_filters: Of filters moeten worden toegevoegd
            auto_column_width: Of kolombreedtes automatisch moeten worden aangepast
            
        Returns:
            Pad naar het opgemaakte Excel-bestand
        """
        try:
            # Laad het workbook
            wb = pd.ExcelFile(excel_path)
            
            # Lees het eerste werkblad
            df = pd.read_excel(wb, sheet_name=0)
            
            # Maak een ExcelWriter object met openpyxl engine
            writer = pd.ExcelWriter(excel_path, engine='openpyxl')
            
            # Schrijf de DataFrame terug naar Excel
            df.to_excel(writer, index=False, sheet_name='Vergelijking')
            
            # Haal het werkblad op
            worksheet = writer.sheets['Vergelijking']
            
            # Voeg filters toe
            if add_filters:
                worksheet.auto_filter.ref = worksheet.dimensions
            
            # Pas kolombreedtes aan
            if auto_column_width:
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    
                    adjusted_width = (max_length + 2) * 1.2
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Sla het bestand op
            writer.close()
            
            return excel_path
        except Exception as e:
            print(f"Fout bij het formatteren van Excel-bestand: {str(e)}")
            return excel_path
