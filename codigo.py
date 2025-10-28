import time
import hashlib
import logging
import sqlite3
import random
from typing import Optional
import requests
from requests.adapters import HTTPAdapter, Retry
import re
from bs4 import BeautifulSoup


# meto la url del destino
URL = "https://salamancadetransportes.com/tiempos-de-llegada/?ref={nParada}"

# Hago los header para simular un navegador y que no a me bloquee la petición
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/129.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://salamancadetransportes.com/",
    "DNT": "1",  # Do Not Track
    "Upgrade-Insecure-Requests": "1",
}


# Creo la sesion con reintentos
def make_session():
    s = requests.Session()
    s.headers.update(HEADERS)
    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s


# Funcion para obtener los datos de la parada
def get_tiempos(parada):
    url = URL.format(nParada=parada)
    s = make_session()
    resp = s.get(url, timeout=15)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    texto = soup.get_text(separator="\n", strip=True)
    
    # Buscar líneas tipo: "Línea 1: 8 minutos"
    patron = re.compile(r"L[íi]nea\s*([0-9A-Za-z]+)\s*:\s*([^\n\r]+)")
    resultados = []
    for linea, tiempo in patron.findall(texto):
        tiempo = tiempo.strip().replace("minutos", "min").replace("minuto", "min")
        resultados.append((linea.strip(), tiempo))

    return resultados

# Ejeccución principal
if __name__ == "__main__":
    try:
        parada = int(input("Número de parada: "))
        datos = get_tiempos(parada)

        print(f"\n📍 Parada {parada} — Resultados:")
        if not datos:
            print(" ❌ (No se encontraron tiempos en la página)")
        else:
            for linea, t in datos:
                print(f"  Línea {linea}: {t}")
        print("-" * 40)

    except Exception as e:
        print("❌ Error:", e)