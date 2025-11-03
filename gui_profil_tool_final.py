# gui_profil_tool_final.py
import requests
from bs4 import BeautifulSoup
import logging 
from typing import Tuple
import tkinter as tk
from tkinter import messagebox

# --- KONFIGURACIJA LOGOVANJA ---
LOG_FILE = 'app_errors.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8', mode='a'), 
        # Loguje samo kritične informacije u datoteku.
    ]
)
logger = logging.getLogger(__name__)

# =========================================================================
# === LOGIKA FUNKCIJA (PEP 8 Konvencije) ===
# =========================================================================

def resetuj_lozinku_sa_kodom(kod_za_resetovanje: str, nova_lozinka: str) -> Tuple[bool, str]:
    """
    Simulira proces resetovanja lozinke (serverska logika).
    Vraća status i poruku.
    """
    validan_kod = "5PBCGi3nCMSGg10rFF2JfQ="
    
    # Prilagođeno logovanje za GUI: logujemo samo greške
    if kod_za_resetovanje == validan_kod: 
        if len(nova_lozinka) >= 8:
            return (True, "LOZINKA JE USPESNO RESETOVANA u simulaciji.")
        else:
            poruka = "Nova lozinka mora imati najmanje 8 znakova."
            logger.error(f"[KORISNIK GRESKA] {poruka}") 
            return (False, f"GRESKA: {poruka}")
    else:
        poruka = "Uneseni kod je nevazeci ili istekao."
        logger.error(f"[KORISNIK GRESKA] {poruka}")
        return (False, f"GRESKA: {poruka}")


def _izvrsi_http_zahtjev(url: str, timeout: int = 5) -> requests.Response:
    """
    Pomoćna funkcija koja izvršava GET zahtev i rukuje svim mrežnim izuzecima.
    Detaljno loguje greške za dev, podiže ConnectionError sa porukom za korisnika.
    """
    try:
        response = requests.get(url, timeout=timeout) 
        response.raise_for_status() 
        return response
        
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        logger.error(f"[DEV LOG - GRESKA HTTP]: URL: {url} | Status: {status_code}", exc_info=True)
        
        # Specifične korisničke poruke
        if status_code == 404:
             user_msg = "Greska 404: Profil nije pronadjen. Proverite ispravnost URL-a."
        elif status_code in (401, 403):
             user_msg = f"Greska {status_code}: Pristup odbijen. Proverite dozvole."
        elif status_code >= 500:
             user_msg = f"Greska {status_code}: Problem sa serverom. Pokusajte ponovo."
        else:
             user_msg = f"HTTP Greska {status_code} (Status: {status_code})."
             
        raise ConnectionError(user_msg) from e

    except requests.exceptions.Timeout as e:
        logger.error(f"[DEV LOG - GRESKA TIMEOUT]: URL: {url} | Vreme: {timeout}s", exc_info=True)
        raise ConnectionError(f"Mrezna Greska (Timeout): Zahtev je istekao nakon {timeout} sekundi. Proverite internet vezu.") from e
        
    except requests.exceptions.ConnectionError as e:
        logger.error(f"[DEV LOG - GRESKA KONEKCIJA]: URL: {url}", exc_info=True)
        # Detaljnija poruka za gaierror/DNS probleme
        if "No address associated with hostname" in str(e):
             raise ConnectionError(f"Mrezna Greska (Konekcija): DNS GRESKA. Proverite da li je adresa ispravna i da li ste povezani na internet.") from e
        else:
             raise ConnectionError(f"Mrezna Greska (Konekcija): Nije moguce uspostaviti vezu. Proverite ispravnost URL-a.") from e

    except requests.exceptions.RequestException as e:
        logger.error(f"[DEV LOG - GRESKA OPSTA]: URL: {url}", exc_info=True)
        raise ConnectionError(f"Mrezna Greska (Nepoznata): Doslo je do neocekivane greske ({e.__class__.__name__}). Pokusajte ponovo.") from e


def dohvati_javne_info(url: str) -> Tuple[str, str]:
    """
    Glavna funkcija za dohvacanje i parsiranje javnih podataka.
    """
    logger.info(f"Pokretanje web scraping-a za URL: {url}")
    
    try:
        response = _izvrsi_http_zahtjev(url)
        
        soup = BeautifulSoup(response.content, "html.parser") 
        
        # Simulacija pronalaska javnih informacija
        # Manja optimizacija kod parsiranja
        ime_element = soup.find('h1', {'class': 'ime'})
        lokacija_element = soup.find('div', {'class': 'lokacija'})
        
        javno_ime = ime_element.text if ime_element else "Nije dostupno (Element imena nije pronadjen)"
        javna_lokacija = lokacija_element.text if lokacija_element else "Nije dostupno (Element lokacije nije pronadjen)"
        
        return javno_ime, javna_lokacija
        
    except ConnectionError as e:
        logger.error(f"[KORISNIK GRESKA] GRESKA PRI DOHVATANJU: {e}")
        return "Greska", str(e)
        
    except Exception as e:
        logger.error(f"[DEV LOG - NEOČEKIVANA GRESKA]: Tip greske: {e.__class__.__name__}", exc_info=True)
        return "Greska", f"Neočekivana greska: {e.__class__.__name__}"


# =========================================================================
# === TKINTER GUI IMPLEMENTACIJA (PEP 8 Konvencije) ===
# =========================================================================

class ProfileToolApp:
    def __init__(self, master):
        self.master = master
        master.title("Python Profil Analiza")
        master.geometry("550x450")

        # Okvir za unos podataka
        input_frame = tk.LabelFrame(master, text="Unos Podataka za Analizu", padx=10, pady=10)
        input_frame.pack(padx=10, pady=10, fill="x")

        # 1. Web Scraping Unos
        tk.Label(input_frame, text="URL za Scraping (npr. https://www.google.com/):").grid(row=0, column=0, sticky="w", pady=5)
        self.url_entry = tk.Entry(input_frame, width=50)
        self.url_entry.insert(0, "https://www.fiktivnistranica.com/profil/test")
        self.url_entry.grid(row=0, column=1, pady=5, padx=5)

        # 2. Password Reset Unos
        tk.Label(input_frame, text="Kod za Reset:").grid(row=1, column=0, sticky="w", pady=5)
        self.kod_entry = tk.Entry(input_frame, width=50)
        self.kod_entry.insert(0, "5PBCGi3nCMSGg10rFF2JfQ=") 
        self.kod_entry.grid(row=1, column=1, pady=5, padx=5)

        tk.Label(input_frame, text="Nova Lozinka:").grid(row=2, column=0, sticky="w", pady=5)
        self.lozinka_entry = tk.Entry(input_frame, width=50, show="*")
        self.lozinka_entry.insert(0, "NovaJakaLozinka123")
        self.lozinka_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # Dugme za pokretanje
        self.run_button = tk.Button(input_frame, text="Pokreni Analizu i Reset", command=self.pokreni_analizu, bg="#4CAF50", fg="white")
        self.run_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Okvir za rezultate
        result_frame = tk.LabelFrame(master, text="Rezultati Analize", padx=10, pady=10)
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.results_text = tk.Text(result_frame, wrap="word", height=10, bg="#f0f0f0")
        self.results_text.pack(fill="both", expand=True)
        self.results_text.insert(tk.END, "Rezultati će biti prikazani ovde...\n")

    def pokreni_analizu(self):
        """
        Dohvaća podatke iz unosa, pokreće funkcije i prikazuje rezultat.
        """
        self.results_text.delete(1.0, tk.END) # Očisti prethodne rezultate
        self.results_text.insert(tk.END, "--- POKRETANJE ---\n")
        
        # 1. Testiranje resetovanja lozinke (PEP 8)
        kod = self.kod_entry.get()
        lozinka = self.lozinka_entry.get()
        
        self.results_text.insert(tk.END, "Simulacija Resetovanja Lozinke...\n")
        status, poruka = resetuj_lozinku_sa_kodom(kod, lozinka)
        
        if status:
            self.results_text.insert(tk.END, f"  [USPEH]: {poruka}\n")
        else:
            self.results_text.insert(tk.END, f"  [NEUSPEH]: {poruka}\n")
            
        self.results_text.insert(tk.END, "\n" + "-"*30 + "\n")

        # 2. Testiranje Web Scrapinga (PEP 8)
        url = self.url_entry.get()
        self.results_text.insert(tk.END, f"Web Scraping (URL: {url})...\n")
        
        ime, lokacija_info = dohvati_javne_info(url)
        
        if ime == "Greska":
            # Koristimo detaljnu poruku iz izuzetka za informisanje korisnika
            self.results_text.insert(tk.END, f"  [GRESKA PRI DOHVATANJU/PARSIRANJU]:\n")
            self.results_text.insert(tk.END, f"  Detalji: {lokacija_info}\n")
        else:
            self.results_text.insert(tk.END, f"  [USPEH - Parsiranje]:\n")
            self.results_text.insert(tk.END, f"  Ime Pronadjeno: {ime}\n")
            self.results_text.insert(tk.END, f"  Lokacija Pronadjena: {lokacija_info}\n")
            
        self.results_text.insert(tk.END, "\n--- ZAVRŠENO ---\n")
        self.results_text.see(tk.END) # Skroluj na dno


if __name__ == "__main__":
    root = tk.Tk()
    app = ProfileToolApp(root)
    root.mainloop()
