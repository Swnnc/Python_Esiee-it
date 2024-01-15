import tkinter as tk
from tkinter import ttk
from collections import Counter
import csv
import requests
from bs4 import BeautifulSoup

class SEO:
    def __init__(self, url, fichier_csv):
        # Initialisation des variables url et fichier parasites
        self.url = url
        self.fichier_csv = fichier_csv

    # Étape 1
    def compter_mots(self, texte):
        # Décomposition du texte en chaine de mots
        mots = texte.split()
        occurrences = Counter(mots)
        # Retourne le nombre d'occurence par ordre décroissant
        mots_tries = sorted(occurrences.items(), key=lambda x: x[1], reverse=True)
        return mots_tries

    # Étape 3
    def mots_csv(self):
        mots_parasites = []
        # Récupère les mots parasites du fichier_csv et les ajoutes dans la liste mots_parasites
        with open(self.fichier_csv, 'r', newline='', encoding='utf-8') as csvfile:
            lecteur_csv = csv.reader(csvfile)
            for ligne in lecteur_csv:
                mots_parasites.extend(ligne)
        return mots_parasites

    # Étape 2
    def del_parasites(self, mots_tries, parasites):
        # Supprime les mots parasites dans la liste de mots_tries
        mots_filtre = [(mot, occurrence) for mot, occurrence in mots_tries if mot not in parasites]
        return mots_filtre

    # Étape 4
    def enlever_balises_html(self, html):
        # Extrait le code source html de l'url
        soup = BeautifulSoup(html, 'html.parser')
        # Extrait le texte du code source. strip retire le superflu en début de texte donc les balises
        texte_sans_balises = soup.get_text(separator=' ', strip=True)
        return texte_sans_balises

    # Étape 6
    def extraire_valeurs_attribut(self, html, balise, attribut):
        # Extrait la ligne spécifique par rapport à la balise et l'attribut indiqué
        valeurs = []
        soup = BeautifulSoup(html, 'html.parser')
        balises = soup.find_all(balise)
        for balise in balises:
            valeur_attribut = balise.get(attribut)
            if valeur_attribut:
                valeurs.append(valeur_attribut)
        return valeurs

    # Étape 8
    def extraire_domaine(self, url):
        # Utilise comme séparateur le '//' d'une url 'https://bm-cat.com'
        try:
            return url.split('/')[2]
        except:
            return url.split('/')[0]

    # Étape 9
    def groupe_domain(self, domain, grp_url):
        # Compare si le domaine est différent
        urls_domaine = [url for url in grp_url if self.extraire_domaine(url) == domain]
        urls_autres = [url for url in grp_url if self.extraire_domaine(url) != domain]
        return urls_domaine, urls_autres

    # Étape 10
    def recuperer_html_depuis_url(self, url):
        response = requests.get(url)
        return response.text

    # Étape 11
    def analyser_referencement(self, mots_cles):
        domain = self.extraire_domaine(self.url)
        html = self.recuperer_html_depuis_url(self.url)
        text = self.enlever_balises_html(html)
        words = self.compter_mots(text)
        words_parasite = self.mots_csv()
        words_filtre = self.del_parasites(words, words_parasite)
        premiers_mots = words_filtre[:4]

        # Nombre de balise alt
        images = self.extraire_valeurs_attribut(html, 'img', 'alt')

        # Liens entrants et sortants
        liens = self.extraire_valeurs_attribut(html, 'a', 'href')
        liens_traite = self.groupe_domain(domain, liens)

        # Vérifie si le mot-clé recherché est présent dans la liste words_filtre
        mots_cles_present = any(mot.lower() in [mot[0].lower() for mot in words_filtre] for mot in mots_cles)

        return {
            "domaine": domain,
            "premiers_mots": premiers_mots,
            "nombre_images": len(images),
            "liens_entrants": len(liens_traite[0]),
            "liens_sortants": len(liens_traite[1]),
            "mots_cles_present": mots_cles_present
        }

class IHMSEO:
    def __init__(self, fenetre):
        self.fenetre = fenetre
        self.fenetre.title("Analyse de Référencement")

        # Création des étiquettes et des champs de saisie
        self.url_label = tk.Label(fenetre, text="URL de la première page :")
        self.url_entry = tk.Entry(fenetre, width=30)

        self.mots_cles_label = tk.Label(fenetre, text="Mot-clé :")
        self.mots_cles_entry = tk.Entry(fenetre, width=30)

        # Création d'un bouton pour l'analyse de référencement
        self.analyser_bouton = tk.Button(fenetre, text="Analyser", command=self.afficher_resultats)

        # Placement des widgets dans la fenêtre
        self.url_label.pack(pady=5)
        self.url_entry.pack(pady=5)

        self.mots_cles_label.pack(pady=5)
        self.mots_cles_entry.pack(pady=5)

        self.analyser_bouton.pack(pady=10)

    # Fonction pour afficher les résultats dans une nouvelle fenêtre
    def afficher_resultats(self):
        url = self.url_entry.get()
        mots_cles = self.mots_cles_entry.get().split(',')

        analyseur = SEO(url=url, fichier_csv="parasite.csv")
        resultats = analyseur.analyser_referencement(mots_cles)

        # Création de la nouvelle fenêtre
        resultat_fenetre = tk.Toplevel(self.fenetre)
        resultat_fenetre.title("Résultats de l'analyse de référencement")

        # Affichage des résultats dans un Treeview
        tree = ttk.Treeview(resultat_fenetre, columns=("Valeur"))
        tree.heading("#0", text="Information")
        tree.heading("Valeur", text="Valeur")

        # Insertion des résultats dans le Treeview
        tree.insert("", "end", text="Domaine", values=(resultats["domaine"],))
        tree.insert("", "end", text="Premiers mots", values=(resultats["premiers_mots"],))
        tree.insert("", "end", text="Nombre d'images", values=(resultats["nombre_images"],))
        tree.insert("", "end", text="Liens entrants", values=(resultats["liens_entrants"],))
        tree.insert("", "end", text="Liens sortants", values=(resultats["liens_sortants"],))
        tree.insert("", "end", text="Mots-clés présents", values=(resultats["mots_cles_present"],))

        # Placement du Treeview dans la nouvelle fenêtre
        tree.pack(expand=True, fill=tk.BOTH)

# Création de la fenêtre principale
fenetre_principale = tk.Tk()
app = IHMSEO(fenetre_principale)

# Lancement de la boucle principale
fenetre_principale.mainloop()