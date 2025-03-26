"""
Module voor het extraheren van tekst uit PDF-bestanden van kwalificatiedossiers.
"""
import os
import re
import PyPDF2
from typing import Dict, List, Tuple, Optional


class PDFExtractor:
    """Klasse voor het extraheren en verwerken van tekst uit kwalificatiedossiers in PDF-formaat."""
    
    def __init__(self, pdf_path: str):
        """
        Initialiseert de PDFExtractor met het pad naar een PDF-bestand.
        
        Args:
            pdf_path: Absoluut pad naar het PDF-bestand
        """
        self.pdf_path = pdf_path
        self.filename = os.path.basename(pdf_path)
        self.text_content = ""
        self.metadata = {}
        
    def extract_text(self) -> str:
        """
        Extraheert alle tekst uit het PDF-bestand.
        
        Returns:
            De geëxtraheerde tekst als string
        """
        text = ""
        try:
            with open(self.pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text() + "\n\n"
            
            self.text_content = text
            return text
        except Exception as e:
            print(f"Fout bij het extraheren van tekst uit {self.filename}: {str(e)}")
            return ""
    
    def extract_metadata(self) -> Dict:
        """
        Extraheert metadata uit het kwalificatiedossier zoals crebonummer, 
        naam, versie, geldigheidsdatum, etc.
        
        Returns:
            Dictionary met metadata
        """
        if not self.text_content:
            self.extract_text()
            
        metadata = {
            "filename": self.filename,
            "crebonr_dossier": self._extract_crebonr_dossier(),
            "crebonr_kwalificatie": self._extract_crebonr_kwalificatie(),
            "naam_kwalificatie": self._extract_naam_kwalificatie(),
            "versie": self._extract_versie(),
            "geldig_vanaf": self._extract_geldig_vanaf()
        }
        
        self.metadata = metadata
        return metadata
    
    def _extract_crebonr_dossier(self) -> str:
        """Extraheert het crebonummer van het kwalificatiedossier."""
        pattern = r"Particuliere beveiliging\s+Crebonr\.\s+(\d+)"
        match = re.search(pattern, self.text_content)
        return match.group(1) if match else ""
    
    def _extract_crebonr_kwalificatie(self) -> str:
        """Extraheert het crebonummer van de kwalificatie."""
        pattern = r"Beveiliger\s*\d*\s*\(Crebonr\.\s+(\d+)\)"
        match = re.search(pattern, self.text_content)
        return match.group(1) if match else ""
    
    def _extract_naam_kwalificatie(self) -> str:
        """Extraheert de naam van de kwalificatie."""
        pattern = r"»\s+(Beveiliger\s*\d*)\s*\(Crebonr"
        match = re.search(pattern, self.text_content)
        return match.group(1) if match else ""
    
    def _extract_versie(self) -> str:
        """Extraheert de versie/wijzigingsjaar van het kwalificatiedossier."""
        pattern = r"Gewijzigd\s+(\d{4})"
        match = re.search(pattern, self.text_content)
        return match.group(1) if match else ""
    
    def _extract_geldig_vanaf(self) -> str:
        """Extraheert de geldigheidsdatum van het kwalificatiedossier."""
        pattern = r"Geldig vanaf\s+(\d{2}-\d{2}-\d{4})"
        match = re.search(pattern, self.text_content)
        return match.group(1) if match else ""
    
    def extract_kerntaken(self) -> List[Dict]:
        """
        Extraheert alle kerntaken uit het kwalificatiedossier.
        
        Returns:
            Lijst van dictionaries met kerntaakinformatie
        """
        if not self.text_content:
            self.extract_text()
            
        kerntaken = []
        # Patroon voor kerntaken (B1-K1, B1-K2, etc.)
        pattern = r"(B\d+-K\d+):\s+([^\n]+)"
        matches = re.finditer(pattern, self.text_content)
        
        for match in matches:
            code = match.group(1)
            naam = match.group(2)
            kerntaken.append({
                "code": code,
                "naam": naam
            })
            
        return kerntaken
    
    def extract_werkprocessen(self) -> List[Dict]:
        """
        Extraheert alle werkprocessen uit het kwalificatiedossier.
        
        Returns:
            Lijst van dictionaries met werkprocesinformatie
        """
        if not self.text_content:
            self.extract_text()
            
        werkprocessen = []
        # Patroon voor werkprocessen (B1-K1-W1, B1-K1-W2, etc.)
        pattern = r"(B\d+-K\d+-W\d+):\s+([^\n]+)"
        matches = re.finditer(pattern, self.text_content)
        
        for match in matches:
            code = match.group(1)
            naam = match.group(2)
            # Bepaal bij welke kerntaak dit werkproces hoort
            kerntaak_code = code.split('-W')[0]
            werkprocessen.append({
                "code": code,
                "naam": naam,
                "kerntaak_code": kerntaak_code
            })
            
        return werkprocessen
    
    def extract_beroepshouding(self) -> str:
        """
        Extraheert de typerende beroepshouding uit het kwalificatiedossier.
        
        Returns:
            Tekst over de typerende beroepshouding
        """
        if not self.text_content:
            self.extract_text()
            
        # Zoek de sectie over typerende beroepshouding
        pattern = r"Typerende beroepshouding(.*?)(?=Resultaat van de beroepsgroep|B\d+-K\d+:)"
        match = re.search(pattern, self.text_content, re.DOTALL)
        return match.group(1).strip() if match else ""
    
    def extract_context(self) -> str:
        """
        Extraheert de context uit het kwalificatiedossier.
        
        Returns:
            Tekst over de context
        """
        if not self.text_content:
            self.extract_text()
            
        # Zoek de sectie over context
        pattern = r"Context(.*?)(?=Typerende beroepshouding)"
        match = re.search(pattern, self.text_content, re.DOTALL)
        return match.group(1).strip() if match else ""
    
    def extract_resultaat(self) -> str:
        """
        Extraheert het resultaat van de beroepsgroep uit het kwalificatiedossier.
        
        Returns:
            Tekst over het resultaat van de beroepsgroep
        """
        if not self.text_content:
            self.extract_text()
            
        # Zoek de sectie over resultaat van de beroepsgroep
        pattern = r"Resultaat van de beroepsgroep(.*?)(?=B\d+-K\d+:|Basisdeel)"
        match = re.search(pattern, self.text_content, re.DOTALL)
        return match.group(1).strip() if match else ""
    
    def extract_vakkennis_vaardigheden(self) -> List[str]:
        """
        Extraheert de vakkennis en vaardigheden uit het kwalificatiedossier.
        
        Returns:
            Lijst van vakkennis en vaardigheden items
        """
        if not self.text_content:
            self.extract_text()
            
        # Zoek de sectie over vakkennis en vaardigheden
        pattern = r"Vakkennis en vaardigheden(.*?)(?=Verantwoordelijkheid en zelfstandigheid|B\d+-K\d+:|2\. Generieke onderdelen)"
        match = re.search(pattern, self.text_content, re.DOTALL)
        
        if not match:
            return []
            
        content = match.group(1).strip()
        
        # Extraheer de individuele items (meestal in bulletpoints)
        items = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('•') or line.startswith('*') or line.startswith('-'):
                items.append(line.lstrip('•*- ').strip())
            elif line.startswith('heeft') or line.startswith('kan'):
                items.append(line.strip())
                
        return [item for item in items if item]
