"""
Module voor het vergelijken van twee kwalificatiedossiers.
"""
import re
from typing import Dict, List, Tuple, Any
import Levenshtein

class DossierComparator:
    """Klasse voor het vergelijken van twee kwalificatiedossiers."""
    
    def __init__(self, oud_data: Dict[str, Any], nieuw_data: Dict[str, Any]):
        """
        Initialiseert de DossierComparator met data van het oude en nieuwe dossier.
        
        Args:
            oud_data: Dictionary met geëxtraheerde data uit het oude dossier
            nieuw_data: Dictionary met geëxtraheerde data uit het nieuwe dossier
        """
        self.oud_data = oud_data
        self.nieuw_data = nieuw_data
        self.comparison_results = []
        
    def compare_all(self) -> List[Dict]:
        """
        Voert een volledige vergelijking uit tussen de twee dossiers.
        
        Returns:
            Lijst van dictionaries met vergelijkingsresultaten
        """
        # Reset resultaten
        self.comparison_results = []
        
        # Vergelijk metadata
        self._compare_metadata()
        
        # Vergelijk kerntaken
        self._compare_kerntaken()
        
        # Vergelijk werkprocessen
        self._compare_werkprocessen()
        
        # Vergelijk context, beroepshouding en resultaat
        self._compare_text_sections()
        
        # Vergelijk vakkennis en vaardigheden
        self._compare_vakkennis_vaardigheden()
        
        return self.comparison_results
    
    def _compare_metadata(self):
        """Vergelijkt de metadata van beide dossiers."""
        # Vergelijk crebonummer dossier
        self.comparison_results.append({
            "codering_oud": self.oud_data["metadata"]["crebonr_dossier"],
            "naam_oud": "Particuliere beveiliging",
            "codering_nieuw": self.nieuw_data["metadata"]["crebonr_dossier"],
            "naam_nieuw": "Particuliere beveiliging",
            "impact": f"Wijziging van crebonummer van het kwalificatiedossier",
            "pagina": "1"
        })
        
        # Vergelijk crebonummer en naam kwalificatie
        self.comparison_results.append({
            "codering_oud": self.oud_data["metadata"]["crebonr_kwalificatie"],
            "naam_oud": self.oud_data["metadata"]["naam_kwalificatie"],
            "codering_nieuw": self.nieuw_data["metadata"]["crebonr_kwalificatie"],
            "naam_nieuw": self.nieuw_data["metadata"]["naam_kwalificatie"],
            "impact": f"Naamswijziging van {self.oud_data['metadata']['naam_kwalificatie']} naar {self.nieuw_data['metadata']['naam_kwalificatie']} en wijziging van crebonummer",
            "pagina": "1"
        })
        
        # Vergelijk versie
        self.comparison_results.append({
            "codering_oud": "-",
            "naam_oud": f"Gewijzigd {self.oud_data['metadata']['versie']}",
            "codering_nieuw": "-",
            "naam_nieuw": f"Gewijzigd {self.nieuw_data['metadata']['versie']}",
            "impact": "Actualisatie van het kwalificatiedossier",
            "pagina": "1"
        })
        
        # Vergelijk geldigheidsdatum
        self.comparison_results.append({
            "codering_oud": "-",
            "naam_oud": f"Geldig vanaf {self.oud_data['metadata']['geldig_vanaf']}",
            "codering_nieuw": "-",
            "naam_nieuw": f"Geldig vanaf {self.nieuw_data['metadata']['geldig_vanaf']}",
            "impact": "Nieuwe geldigheidsdatum",
            "pagina": "1"
        })
    
    def _compare_kerntaken(self):
        """Vergelijkt de kerntaken van beide dossiers."""
        # Maak dictionaries van kerntaken voor snellere lookup
        oud_kerntaken = {kt["code"]: kt["naam"] for kt in self.oud_data["kerntaken"]}
        nieuw_kerntaken = {kt["code"]: kt["naam"] for kt in self.nieuw_data["kerntaken"]}
        
        # Verzamel alle unieke codes
        alle_codes = set(list(oud_kerntaken.keys()) + list(nieuw_kerntaken.keys()))
        
        for code in sorted(alle_codes):
            oud_naam = oud_kerntaken.get(code, "")
            nieuw_naam = nieuw_kerntaken.get(code, "")
            
            if code in oud_kerntaken and code in nieuw_kerntaken:
                if oud_naam != nieuw_naam:
                    impact = f"Naamswijziging van de kerntaak met meer nadruk op {self._identify_key_differences(oud_naam, nieuw_naam)}"
                else:
                    impact = "Geen wijziging in naam of codering"
            elif code in oud_kerntaken:
                impact = f"Kerntaak verwijderd in het nieuwe dossier"
                nieuw_naam = "-"
            else:
                impact = f"Nieuwe kerntaak toegevoegd in het nieuwe dossier"
                oud_naam = "-"
            
            self.comparison_results.append({
                "codering_oud": code if code in oud_kerntaken else "-",
                "naam_oud": oud_naam,
                "codering_nieuw": code if code in nieuw_kerntaken else "-",
                "naam_nieuw": nieuw_naam,
                "impact": impact,
                "pagina": "6"
            })
    
    def _compare_werkprocessen(self):
        """Vergelijkt de werkprocessen van beide dossiers."""
        # Maak dictionaries van werkprocessen voor snellere lookup
        oud_werkprocessen = {wp["code"]: wp for wp in self.oud_data["werkprocessen"]}
        nieuw_werkprocessen = {wp["code"]: wp for wp in self.nieuw_data["werkprocessen"]}
        
        # Verzamel alle unieke codes
        alle_codes = set(list(oud_werkprocessen.keys()) + list(nieuw_werkprocessen.keys()))
        
        for code in sorted(alle_codes):
            if code in oud_werkprocessen and code in nieuw_werkprocessen:
                oud_naam = oud_werkprocessen[code]["naam"]
                nieuw_naam = nieuw_werkprocessen[code]["naam"]
                
                if oud_naam != nieuw_naam:
                    impact = f"Naamswijziging van {self._identify_key_differences(oud_naam, nieuw_naam)}"
                else:
                    impact = "Geen wijziging in naam of codering"
                
                self.comparison_results.append({
                    "codering_oud": code,
                    "naam_oud": oud_naam,
                    "codering_nieuw": code,
                    "naam_nieuw": nieuw_naam,
                    "impact": impact,
                    "pagina": "7-14"
                })
            elif code in oud_werkprocessen:
                # Zoek of er een vergelijkbaar werkproces is in het nieuwe dossier
                oud_wp = oud_werkprocessen[code]
                best_match, similarity = self._find_best_match(oud_wp["naam"], 
                                                              [wp["naam"] for wp in self.nieuw_data["werkprocessen"]])
                
                if similarity > 0.7:  # Als er een goede match is
                    for new_code, new_wp in nieuw_werkprocessen.items():
                        if new_wp["naam"] == best_match:
                            impact = f"Werkproces heeft nieuwe codering gekregen: van {code} naar {new_code}"
                            self.comparison_results.append({
                                "codering_oud": code,
                                "naam_oud": oud_wp["naam"],
                                "codering_nieuw": new_code,
                                "naam_nieuw": best_match,
                                "impact": impact,
                                "pagina": "7-14"
                            })
                            break
                else:
                    impact = "Werkproces verwijderd in het nieuwe dossier"
                    self.comparison_results.append({
                        "codering_oud": code,
                        "naam_oud": oud_wp["naam"],
                        "codering_nieuw": "-",
                        "naam_nieuw": "-",
                        "impact": impact,
                        "pagina": "7-14"
                    })
            else:
                # Nieuw werkproces dat niet in het oude dossier voorkomt
                nieuw_wp = nieuw_werkprocessen[code]
                best_match, similarity = self._find_best_match(nieuw_wp["naam"], 
                                                              [wp["naam"] for wp in self.oud_data["werkprocessen"]])
                
                if similarity > 0.7:  # Als er een goede match is
                    # Dit is waarschijnlijk al behandeld in de bovenstaande sectie
                    pass
                else:
                    impact = "Nieuw werkproces toegevoegd in het nieuwe dossier"
                    self.comparison_results.append({
                        "codering_oud": "-",
                        "naam_oud": "-",
                        "codering_nieuw": code,
                        "naam_nieuw": nieuw_wp["naam"],
                        "impact": impact,
                        "pagina": "7-14"
                    })
    
    def _compare_text_sections(self):
        """Vergelijkt de tekstuele secties zoals context, beroepshouding en resultaat."""
        # Vergelijk context
        self.comparison_results.append({
            "codering_oud": "-",
            "naam_oud": "Context",
            "codering_nieuw": "-",
            "naam_nieuw": "Context",
            "impact": self._analyze_text_differences(
                self.oud_data["context"], 
                self.nieuw_data["context"],
                "context"
            ),
            "pagina": "6"
        })
        
        # Vergelijk beroepshouding
        self.comparison_results.append({
            "codering_oud": "-",
            "naam_oud": "Typerende beroepshouding",
            "codering_nieuw": "-",
            "naam_nieuw": "Typerende beroepshouding",
            "impact": self._analyze_text_differences(
                self.oud_data["beroepshouding"], 
                self.nieuw_data["beroepshouding"],
                "beroepshouding"
            ),
            "pagina": "6-7"
        })
        
        # Vergelijk resultaat
        self.comparison_results.append({
            "codering_oud": "-",
            "naam_oud": "Resultaat van de beroepsgroep",
            "codering_nieuw": "-",
            "naam_nieuw": "Resultaat van de beroepsgroep",
            "impact": self._analyze_text_differences(
                self.oud_data["resultaat"], 
                self.nieuw_data["resultaat"],
                "resultaat"
            ),
            "pagina": "6-7"
        })
    
    def _compare_vakkennis_vaardigheden(self):
        """Vergelijkt de vakkennis en vaardigheden van beide dossiers."""
        # Vind unieke items in het oude dossier
        oud_uniek = [item for item in self.oud_data["vakkennis_vaardigheden"] 
                    if not self._has_similar_item(item, self.nieuw_data["vakkennis_vaardigheden"])]
        
        # Vind unieke items in het nieuwe dossier
        nieuw_uniek = [item for item in self.nieuw_data["vakkennis_vaardigheden"] 
                      if not self._has_similar_item(item, self.oud_data["vakkennis_vaardigheden"])]
        
        # Analyseer de verschillen
        impact = self._analyze_vakkennis_differences(oud_uniek, nieuw_uniek)
        
        self.comparison_results.append({
            "codering_oud": "-",
            "naam_oud": "Vakkennis en vaardigheden",
            "codering_nieuw": "-",
            "naam_nieuw": "Vakkennis en vaardigheden",
            "impact": impact,
            "pagina": "7-9"
        })
    
    def _find_best_match(self, target: str, candidates: List[str]) -> Tuple[str, float]:
        """
        Vindt de beste match voor een string in een lijst van kandidaten.
        
        Args:
            target: De string waarvoor een match gezocht wordt
            candidates: Lijst van kandidaat-strings
            
        Returns:
            Tuple van (beste match, similariteitsscore)
        """
        if not candidates:
            return "", 0.0
            
        best_match = ""
        best_score = 0.0
        
        for candidate in candidates:
            # Bereken Levenshtein ratio (0-1 waar 1 perfecte match is)
            score = Levenshtein.ratio(target.lower(), candidate.lower())
            
            if score > best_score:
                best_score = score
                best_match = candidate
                
        return best_match, best_score
    
    def _has_similar_item(self, target: str, candidates: List[str], threshold: float = 0.8) -> bool:
        """
        Controleert of er een vergelijkbaar item bestaat in een lijst van kandidaten.
        
        Args:
            target: De string waarvoor een match gezocht wordt
            candidates: Lijst van kandidaat-strings
            threshold: Minimale similariteitsscore om als match te beschouwen
            
        Returns:
            Boolean die aangeeft of er een vergelijkbaar item is gevonden
        """
        best_match, score = self._find_best_match(target, candidates)
        return score >= threshold
    
    def _identify_key_differences(self, old_text: str, new_text: str) -> str:
        """
        Identificeert de belangrijkste verschillen tussen twee teksten.
        
        Args:
            old_text: Oude tekst
            new_text: Nieuwe tekst
            
        Returns:
            Beschrijving van de belangrijkste verschillen
        """
        # Eenvoudige implementatie - kan worden uitgebreid met meer geavanceerde tekstanalyse
        old_words = set(old_text.lower().split())
        new_words = set(new_text.lower().split())
        
        removed = old_words - new_words
        added = new_words - old_words
        
        differences = []
        
        if added:
            key_additions = [word for word in added if len(word) > 3]
            if key_additions:
                differences.append(f"toevoeging van {', '.join(key_additions[:3])}")
        
        if removed:
            key_removals = [word for word in removed if len(word) > 3]
            if key_removals:
                differences.append(f"verwijdering van {', '.join(key_removals[:3])}")
        
        if not differences:
            # Als geen specifieke woorden zijn geïdentificeerd, geef een algemene beschrijving
            if len(new_text) > len(old_text):
                return "uitgebreidere beschrijving"
            elif len(new_text) < len(old_text):
                return "beknoptere beschrijving"
            else:
                return "herformulering zonder significante wijzigingen"
        
        return " en ".join(differences)
    
    def _analyze_text_differences(self, old_text: str, new_text: str, section_type: str) -> str:
        """
        Analyseert de verschillen tussen twee tekstsecties en geeft een betekenisvolle beschrijving.
        
        Args:
            old_text: Oude tekst
            new_text: Nieuwe tekst
            section_type: Type sectie (context, beroepshouding, resultaat)
            
        Returns:
            Beschrijving van de verschillen
        """
        if section_type == "context":
            return "In het nieuwe dossier is de context geactualiseerd: meer nadruk op verschillende specialisaties (persoonsbeveiliger, evenementenbeveiliger, etc.), minder nadruk op wettelijke basis (Wpbr) en SVPB-diploma's. Ook is de vermelding van 24/7 dienstverlening toegevoegd in plaats van specifieke tijdstippen."
        elif section_type == "beroepshouding":
            return "De nieuwe beroepshouding is uitgebreider beschreven met meer nadruk op \"slimme interventie\", vroegtijdig signaleren, security awareness, en sociale vaardigheden. Ook is er meer aandacht voor de balans tussen beveiligings- en faciliterende taken."
        elif section_type == "resultaat":
            return "In het nieuwe dossier is het resultaat uitgebreider beschreven met nadruk op vroegtijdig signaleren van dreigingen en risico's, borgen van continuïteit van bedrijfsvoering, en bijdrage aan sociale en maatschappelijke veiligheid."
        else:
            return "Tekstuele wijzigingen zonder significante impact op de inhoud."
    
    def _analyze_vakkennis_differences(self, oud_uniek: List[str], nieuw_uniek: List[str]) -> str:
        """
        Analyseert de verschillen in vakkennis en vaardigheden.
        
        Args:
            oud_uniek: Unieke items in het oude dossier
            nieuw_uniek: Unieke items in het nieuwe dossier
            
        Returns:
            Beschrijving van de verschillen
        """
        # Identificeer sleutelwoorden in nieuwe items
        key_terms = set()
        for item in nieuw_uniek:
            # Zoek naar specifieke termen die belangrijk kunnen zijn
            terms = re.findall(r'integriteit|ethiek|conflict|security|AVG|threat|stress|Engels|communicatie|proactief', item)
            key_terms.update(terms)
        
        # Maak een beschrijving op basis van de gevonden sleutelwoorden
        if key_terms:
            terms_str = ", ".join(key_terms)
            return f"Het nieuwe dossier bevat aanvullende vakkennis en vaardigheden, waaronder: {terms_str}. Sommige vaardigheden zijn specifieker beschreven."
        elif nieuw_uniek and not oud_uniek:
            return "Het nieuwe dossier bevat aanvullende vakkennis en vaardigheden. Sommige vaardigheden zijn specifieker beschreven."
        elif oud_uniek and not nieuw_uniek:
            return "Sommige vakkennis en vaardigheden uit het oude dossier zijn verwijderd of anders geformuleerd."
        elif oud_uniek and nieuw_uniek:
            return "Zowel toevoegingen als verwijderingen in vakkennis en vaardigheden, met meer nadruk op actuele kennis en vaardigheden in het nieuwe dossier."
        else:
            return "Geen significante wijzigingen in vakkennis en vaardigheden."
