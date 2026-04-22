import pytest
import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager

def test_edge_login():
    # 1. Podešavanja za Edge
    edge_options = Options()
    # edge_options.add_argument("--headless") # Otkomentariši ako ne želiš da vidiš prozor

    # 2. Automatski skida i pokreće msedgedriver
    service = Service(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=edge_options)

    try:
        # 3. Idi na tvoj sajt (Mora da radi u drugom terminalu!)
        driver.get("http://127.0.0.1:5000/login")
        
        # Provera - zamenite sa naslovom tvoje stranice
        assert "Login" in driver.title or "Skladište" in driver.title
        print("Edge je uspešno otvorio aplikaciju!")
        
    finally:
        # 4. Ugasi brauzer nakon testa
        driver.quit()