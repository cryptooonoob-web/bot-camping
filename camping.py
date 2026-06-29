import time
import requests
from playwright.sync_api import sync_playwright

# --- CONFIGURATION ---
URL_CAMPING = "https://www.capfun.com/camping-france-aquitaine-lou_castel-FR.html"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1521224736540201072/wQRTsLqVQ9WcZru2Mdn4-LaoT3rIlROGogQXbRvMI4DkuU01uBaEM2Cg5KbTmJ9OZuOk"

# NOM EXACT DU MOBIL-HOME
NOM_MOBIL_HOME = "ROSE TOP PRESTA 4 PERS"

def send_discord_message(prix):
    data = {
        "content": f"🏕️ **Alerte Capfun !** Le prix actuel en Août du **{NOM_MOBIL_HOME}** est de : **{prix}**"
    }
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print("Notification envoyée sur Discord ! 🚀")
        else:
            print(f"Erreur Webhook Discord : {response.status_code}")
    except Exception as e:
        print(f"Impossible d'envoyer le message à Discord : {e}")

def check_price():
    print("Ouverture du navigateur...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=50)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        
        print("Chargement de la page de Capfun...")
        page.goto(URL_CAMPING, wait_until="domcontentloaded")
        
        # Pause initiale
        time.sleep(4)
        
        # --- AJOUT : CLIC SUR L'ONGLET AOUT ---
        try:
            print("Bascule sur l'onglet AOUT...")
            # On cherche l'onglet qui contient précisément le texte "AOUT" ou "AOÛT"
            onglet_aout = page.locator("text=AOUT")
            
            # Si le site l'écrit avec un accent, on prévoit une alternative
            if onglet_aout.count() == 0:
                onglet_aout = page.locator("text=AOÛT")
                
            onglet_aout.click()
            print("Onglet cliqué ! Attente de la mise à jour des prix...")
            time.sleep(3) # On laisse 3 secondes au tableau pour afficher Août
            
        except Exception as e:
            print(f"⚠️ Impossible de cliquer sur l'onglet AOUT, tentative de lecture directe... ({e})")

        try:
            print(f"Recherche de la ligne : '{NOM_MOBIL_HOME}'...")
            ligne_mobil_home = page.locator("tr", has_text=NOM_MOBIL_HOME).first
            ligne_mobil_home.wait_for(state="attached", timeout=10000)
            
            # .last prend la case la plus à droite (fin août). 
            # Si c'est au début du mois d'août, on pourra changer par .first ou l'index de la colonne.
            case_prix = ligne_mobil_home.locator("td.tableau-resa-jaune span.rouge").last
            
            prix_brut = case_prix.inner_text().strip()
            
            if prix_brut:
                montant = prix_brut if "€" in prix_brut else f"{prix_brut} €"
                print(f"\n🎉 SUCCÈS DYNAMIQUE ! Le prix trouvé en Août est de : {montant}")
                send_discord_message(montant)
            else:
                print("\n❌ La ligne existe mais la case est vide.")
                
        except Exception as e:
            print(f"\n❌ ÉCHEC : Impossible de trouver le prix pour '{NOM_MOBIL_HOME}'.")
            print(f"Détails : {e}")
            
        time.sleep(3)
        browser.close()

if __name__ == "__main__":
    check_price()
