#!/usr/bin/python3
# -*- coding: utf-8 -*-
# PEP 263 Compliant: Encoding declaration for Unicode compatibility.
import requests
from bs4 import BeautifulSoup
import time
import sys
import logging 
from typing import Tuple

# --- PODEŠAVANJE LOGOVANJA ---
LOG_FILE = 'app_errors.log'

# Konfigurisanje logovanja: šalje ERROR poruke u datoteku, a sve ostalo na konzolu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8', mode='a'), 
        logging.StreamHandler(sys.stdout) # Sve logger poruke idu na konzolu
    ]
)
logger = logging.getLogger(__name__)

# --- 1. PASSWORD RESET SIMULATION (Optimizovani Log) ---

def resetuj_lozinku_sa_kodom(kod_za_resetovanje: str, nova_lozinka: str) -> bool:
    """
    Simulira proces resetovanja lozinke (serverska logika),
    s optimizovanim logovanjem.
    """
    
    logger.info("\n--- Pokretanje simulacije resetovanja lozinke ---")
    
    validan_kod = "5PBCGi3nCMSGg10rFF2JfQ="
    
    if kod_za_resetovanje == validan_kod: 
        logger.info(f"[{time.strftime('%H:%M:%S')}] Kod je validan.")
        time.sleep(0.5)
        
        if len(nova_lozinka) >= 8:
            logger.info(f"[{time.strftime('%H:%M:%S')}] Lozinka je jaka. Postavljanje...")
            time.sleep(0.5)
            logger.info("LOZINKA JE USPESNO RESETOVANA U SIMULACIJI.")
            return True
        else:
            poruka = "Nova lozinka mora imati najmanje 8 znakova."
            logger.error(f"[KORISNIK GRESKA] {poruka}") 
            return False
    else:
        poruka = "Uneseni kod je nevazeci ili istekao."
        logger.error(f"[KORISNIK GRESKA] {poruka}")
        return False


# --- 2. ETHICAL PUBLIC DATA WEB SCRAPING (Finalni oblik sa specifičnim porukama) ---

def _izvrsi_http_zahtjev(url: str, timeout: int = 5) -> requests.Response:
    """
    Pomocna funkcija koja izvrsava GET zahtev i rukuje svim mrežnim izuzecima.
    Sadrži vrlo specificne poruke o greskama za korisnika.
    """
    try:
        response = requests.get(url, timeout=timeout) 
        response.raise_for_status() 
        return response
        
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        logger.error(f"[DEV LOG - GRESKA HTTP]: URL: {url} | Status: {status_code} | Tip greske: {e.__class__.__name__}", exc_info=True)
        
        # SPECIFIČNA KORISNIČKA PORUKA za HTTP greške
        if status_code == 404:
             user_msg = "Greska 404: Profil nije pronadjen. Proverite ispravnost koda profila."
        elif status_code in (401, 403):
             user_msg = f"Greska {status_code}: Pristup odbijen. Proverite da li imate potrebne dozvole ili da li je profil privatan."
        elif status_code >= 500:
             user_msg = f"Greska {status_code}: Problem sa serverom. Pokusajte ponovo za nekoliko minuta."
        else:
             user_msg = f"HTTP Greska {status_code}. Proverite da li profil postoji."
             
        raise ConnectionError(user_msg) from e

    except requests.exceptions.Timeout as e:
        logger.error(f"[DEV LOG - GRESKA TIMEOUT]: URL: {url} | Vreme: {timeout}s | Tip greske: {e.__class__.__name__}", exc_info=True)
        # SPECIFIČNA KORISNIČKA PORUKA za Timeout
        raise ConnectionError(f"Mrezna Greska (Timeout): Zahtev je istekao nakon {timeout} sekundi. Preporuka: Proverite vasu internet vezu ili privremeno iskljucite VPN/Proxy.") from e
        
    except requests.exceptions.ConnectionError as e:
        logger.error(f"[DEV LOG - GRESKA KONEKCIJA]: URL: {url} | Tip greske: {e.__class__.__name__}", exc_info=True)
        # SPECIFIČNA KORISNIČKA PORUKA za Konekciju
        raise ConnectionError(f"Mrezna Greska (Konekcija): Nije moguce uspostaviti vezu sa serverom. Preporuka: Proverite da li je URL ispravan ili da li vas firewall blokira aplikaciju.") from e

    except requests.exceptions.RequestException as e:
        logger.error(f"[DEV LOG - GRESKA OPSTA]: URL: {url} | Tip greske: {e.__class__.__name__}", exc_info=True)
        # SPECIFIČNA KORISNIČKA PORUKA za Opštu grešku
        raise ConnectionError(f"Mrezna Greska (Nepoznata): Doslo je do neocekivane greske ({e.__class__.__name__}). Pokusajte ponovo.") from e

def dohvati_javne_info_optimizovano(profil_kod: str) -> Tuple[str, str]:
    """
    Glavna funkcija za dohvacanje i parsiranje javnih podataka.
    """
    
    logger.info("\n--- Pokretanje etickog web scraping-a javnih podataka ---")
    url = f"https://www.fiktivnistranica.com/profil/{profil_kod}"
    
    try:
        response = _izvrsi_http_zahtjev(url)
        
        # Parsiranje HTML-a (BeautifulSoup)
        soup = BeautifulSoup(response.content, "html.parser") 
        
        javna_lokacija = soup.find('div', {'class': 'lokacija'}).text if soup.find('div', {'class': 'lokacija'}) else "Nije dostupno (Element lokacije nije pronadjen)"
        javno_ime = soup.find('h1', {'class': 'ime'}).text if soup.find('h1', {'class': 'ime'}) else "Nije dostupno (Element imena nije pronadjen)"
        
        logger.info("Podaci uspesno obradjeni (Fiktivni podaci)")
        return javno_ime, javna_lokacija
        
    except ConnectionError as e:
        # Hvatanje podignutih izuzetaka s prilagodjenim, specificnim porukama
        print(f"[KORISNIK GRESKA] GRESKA PRI DOHVATANJU: {e}")
        return "Greska", "Mreza/HTTP Greska"
        
    except Exception as e:
        # Hvatanje neocekivanih gresaka (npr. greska u parsiranju)
        logger.error(f"[DEV LOG - NEOČEKIVANA GRESKA]: Tip greske: {e.__class__.__name__}", exc_info=True)
        print(f"[KORISNIK GRESKA] Doslo je do neocekivane greske u parsiranju. Detalji: {e.__class__.__name__}")
        return "Greska", "Parsiranje/Interna Greska"


# --- PRIMJER UPOTREBE (GLAVNI DEO KODA) ---
if __name__ == "__main__":
    
    # Potrebna instalacija: pip install requests beautifulsoup4
    
    logger.info("==========================================")
    logger.info("      TESTIRANJE SVIH FUNKCIJA           ")
    logger.info("==========================================")
    
    # TEST 1: Resetovanje lozinke (Uspjeh)
    reset_kod = "5PBCGi3nCMSGg10rFF2JfQ="
    nova_lozinka = "TajniKod456!"
    resetuj_lozinku_sa_kodom(reset_kod, nova_lozinka)
    
    # TEST 2: Web Scraping (Simulacija)
    profil_kod_za_test = "userprofile123"
    
    ime, lokacija = dohvati_javne_info_optimizovano(profil_kod_za_test)
    
    print("\nREZULTAT WEB SCRAPINGA:")
    print(f"Ime profila: {ime}")
    print(f"Lokacija: {lokacija}")

