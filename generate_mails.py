#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génération des 273 mails de prospection Harmonie Yacht.
Skip les 10 premiers leads déjà traités.
Sortie : mails-tous-personnalises.txt + gmass-yamm-import.csv
"""
import csv
import re
from pathlib import Path

ROOT = Path("/home/user/robinai-prospection")
SRC = ROOT / "entreprises-seminaires-montpellier.csv"
OUT_TXT = ROOT / "mails-tous-personnalises.txt"
OUT_CSV = ROOT / "gmass-yamm-import.csv"

# Leads déjà traités (Phase 1) — à skipper
ALREADY_DONE = {
    "Centre Porsche Montpellier",
    "Poncet & Poncet Christie's",
    "Ferrini BTP",
    "Solandis",
    "Cabiron Traiteur",
    "Manava Wedding",
    "Domaine de l'Hortus",
    "Château Puech-Haut",
    "Aurea Avocats",
    "Agence Dugas",
}

# ---------- Distance ----------
DIST_MAP = {
    "Montpellier": "à 15 min",
    "Lattes": "à 10 min",
    "Mauguio": "à 10 min",
    "Pérols": "à 5 min",
    "Castelnau-le-Lez": "à 20 min",
    "Le Crès": "à 20 min",
    "Jacou": "à 20 min",
    "Clapiers": "à 20 min",
    "Vendargues": "à 20 min",
    "Baillargues": "à 20 min",
    "Saint-Jean-de-Védas": "à 20 min",
    "Castries": "à 20 min",
    "Fabrègues": "à 20 min",
    "Saint-Gély-du-Fesc": "à 25 min",
    "Combaillaux": "à 25 min",
    "Montferrier-sur-Lez": "à 25 min",
    "Juvignac": "à 25 min",
    "Saint-Clément-de-Rivière": "à 25 min",
    "Frontignan": "à 30 min",
    "Lunel": "à 30 min",
    "Sète": "à 30-35 min",
    "Villeneuve-lès-Maguelone": "à 30-35 min",
    "Palavas-les-Flots": "à 30-35 min",
    "Cap d'Agde": "à 45 min",
    "Pézenas": "à 45 min",
    "Aniane": "à 45 min",
    "Valflaunès": "à 45 min",
    "Lauret": "à 45 min",
    "Saint-Mathieu-de-Tréviers": "à 45 min",
    "Saint-Drézéry": "à 30 min",
    "Saint-Bauzille-de-Montmel": "à 35 min",
    "Saint-Jean-de-Cuculles": "à 45 min",
    "Saint-Jean-de-Fos": "à 50 min",
    "Saint-Georges-d'Orques": "à 25 min",
    "Cournonterral": "à 30 min",
    "Gigean": "à 30 min",
    "Mèze": "à 35 min",
    "Villeveyrac": "à 40 min",
    "Castelnau-de-Guers": "à 45 min",
    "Cazouls-lès-Béziers": "à 1h",
    "Vacquières": "à 50 min",
    "Béziers": "à 1h",
    "Faugères": "à 1h",
    "Saint-Chinian": "à 1h",
    "Ganges": "à 1h",
    "Lodève": "à 1h",
    "Clermont-l'Hérault": "à 1h",
    "Maraussan": "à 1h",
    "Cabrerolles": "à 1h",
    "Berlou": "à 1h",
    "Puimisson": "à 1h",
    "Puissalicon": "à 1h",
    "Thézan-lès-Béziers": "à 1h",
    "Villeneuve-lès-Béziers": "à 1h",
    "Notre-Dame-de-Londres": "à 50 min",
    "Saint-Martin-de-Londres": "à 50 min",
    "Saint-André-de-Sangonis": "à 50 min",
    "Montpeyroux": "à 1h",
    "Ceyras": "à 1h",
    "Jonquières": "à 1h-1h15",
}


def get_distance(ville: str) -> str:
    return DIST_MAP.get(ville, "à 1h")


# ---------- Salutation ----------
GENERIC_PREFIXES = {
    "contact", "info", "infos", "hello", "bienvenue", "accueil", "cabinet",
    "courtier", "courtiers", "rgpd", "service", "serviceclient", "agence",
    "montpellier", "beziers", "lunel", "sete", "lattes", "traiteur",
    "domaine", "domainecastan", "domainepradines", "caveau", "clos",
    "herail-assurances", "sarlravaldec", "ajmtraiteur", "madamepari",
    "restaurantquaidenface", "maisonbonnaire", "pastiscontact", "pac-contact",
    "reseaux-sociaux", "so2fi", "lugagne", "lugagne.delpon", "tourisme",
    "demande", "ts",
}

# Map prénom (extraits) — accent
PRENOM_FIX = {
    "clementine": "Clémentine",
    "celine": "Céline",
    "veronique": "Véronique",
    "rocafull": None,  # nom de famille => générique
    "molina": None,
    "frederic": "Frédéric",
    "rudy": "Rudy",
    "mary": "Mary",
    "sebastien": "Sébastien",
    "sebastien.haspot": "Sébastien",
    "sebastien.avallone": "Sébastien",
    "ophelie": "Ophélie",
    "marie": "Marie",
    "marie.bertrand": "Marie",
    "carole": "Carole",
    "alexandre": "Alexandre",
    "alexandre.richard": "Alexandre",
    "thierry": "Thierry",
    "thierry.carrie": "Thierry",
    "yoan": "Yoan",
    "yoan.rethore": "Yoan",
    "magalie": "Magalie",
    "magalie.favier": "Magalie",
    "roland": "Roland",
    "roland.dupaquier": "Roland",
    "eric": "Éric",
    "eric.bertaud34": "Éric",
    "gael": "Gaël",
    "gael.dubois": "Gaël",
    "laetitia": "Laëtitia",
    "martin": "Martin",
    "cmazel": None,
    "jf": None,
    "jf.coutelou": None,
    "lunel": None,
    "celinevila": "Céline",
    "lunel@lfccourtage": None,
    "bchevalier": None,
    "othoniel": None,
    "lasmoles-avocat": None,
    "retyfernandez": None,
    "lugagne.delpon": None,
}

KNOWN_FIRST = {
    "clementine", "celine", "veronique", "frederic", "rudy", "mary",
    "sebastien", "ophelie", "marie", "carole", "alexandre", "thierry",
    "yoan", "magalie", "roland", "eric", "gael", "laetitia", "martin",
    "celinevila",
}


def get_salut(email: str) -> str:
    """Retourne 'Bonjour {Prenom},' ou 'Bonjour,'"""
    if not email:
        return "Bonjour,"
    local = email.split("@")[0].lower().strip()
    # Cas connus
    if local in KNOWN_FIRST:
        return f"Bonjour {PRENOM_FIX[local]},"
    # Si commence par un prénom connu suivi de . ou _
    for first in KNOWN_FIRST:
        if local.startswith(first + ".") or local.startswith(first + "_") or local == first:
            return f"Bonjour {PRENOM_FIX[first]},"
    # Si est un prénom simple (pas de . pas de chiffre)
    if local in GENERIC_PREFIXES:
        return "Bonjour,"
    return "Bonjour,"


# ---------- Segmentation ----------
def get_segment(secteur: str, nom: str) -> str:
    s = secteur.strip()
    if s in {"CGP", "Concession auto premium", "Hôtellerie 5 étoiles",
             "Hôtellerie 5 etoiles", "Immobilier prestige", "Promoteur immobilier"}:
        return "A"
    if s in {"BTP", "EnR", "Climatisation", "Industrie", "Logistique",
             "Bureau d'études", "Expert-comptable", "Cabinet recrutement",
             "Courtage assurance", "Courtage crédit", "Courtage énergie",
             "Courtage travaux", "Cabinet conseil RH", "Cabinet conseil"}:
        return "B"
    if s in {"Wedding planner", "Agence événementielle", "Hôtellerie", "Traiteur"}:
        return "C"
    if s == "Viticulture":
        return "D"
    # Restauration : si traiteur dans le nom -> C, sinon E
    if s == "Restauration":
        if "traiteur" in nom.lower():
            return "C"
        return "E"
    # E par défaut
    return "E"


SEG_LIBELLE = {
    "A": "Cadeau client VIP",
    "B": "Séminaire interne",
    "C": "Partenaire revendeur",
    "D": "Œnotourisme",
    "E": "Indépendants culturels",
}


# ---------- TOP leads (hooks personnalisés via connaissance/heuristique) ----------
# Pour chaque lead TOP : (hook, [override_objet?])
TOP_HOOKS = {
    # ==== CGP ====
    "Groupe Sarro": "Cabinet de gestion de patrimoine indépendant à Jacou — votre clientèle vous suit pour la qualité du conseil et la durée de la relation.",
    "Génération & Patrimoine": "Cabinet de gestion privée à Saint-Jean-de-Védas — une approche transversale du patrimoine qui crée un lien fort avec vos clients.",
    "Eminence Patrimoine": "Cabinet de gestion de patrimoine à Castelnau-le-Lez — vos clients vous confient bien plus qu'un dossier financier.",
    "Cabinet CIEM": "Cabinet CIEM à Lattes — un accompagnement patrimonial où la confiance se construit sur des années.",
    "Capfinances Montpellier": "Capfinances à Lattes — un réseau qui s'est imposé sur le conseil patrimonial indépendant.",
    "Carré des Guilhem": "Cabinet de gestion privée à Montferrier-sur-Lez — une approche soignée du patrimoine, dans un cadre qui vous ressemble.",
    "Hyuman": "Hyuman à Lattes — un cabinet qui place l'humain au cœur du conseil patrimonial.",
    "Investir Patrimoine": "Cabinet Investir Patrimoine à Montpellier — vos clients comptent sur vous pour les moments-clés de leur vie financière.",
    "Senzo Conseil": "Senzo Conseil à Montpellier — un cabinet où la relation client se cultive sur le long terme.",
    "Aristote Patrimoine": "Aristote Patrimoine à Lattes — la sagesse en gestion de patrimoine, jusque dans le nom.",
    "Acte Patrimoine Stéphane Gay": "Cabinet de gestion privée à Saint-Bauzille-de-Montmel — un accompagnement patrimonial sur-mesure pour vos clients.",
    "Selexium Montpellier": "Selexium à Montpellier — un réseau national de CGP avec une vraie présence terrain ici.",
    "LGP Conseil": "LGP Conseil à Cournonterral — un cabinet qui mise sur la proximité avec ses clients.",
    "Olifan Group Montpellier": "Olifan Group à Mauguio — un acteur national de la gestion privée avec une équipe locale solide.",
    "Patrimonial Conseil": "Patrimonial Conseil à Montpellier — vos clients vous confient leur projet de vie, pas qu'un placement.",
    "Quintésens Montpellier": "Quintésens à Montpellier — un réseau structuré de conseil patrimonial avec l'œil de l'indépendant.",
    "Valetys Montpellier": "Valetys Montpellier — vos clients premium attendent un accompagnement à la hauteur du patrimoine confié.",
    "Valetys Béziers": "Valetys Béziers — une présence forte sur l'Ouest héraultais auprès d'une clientèle exigeante.",
    "Johnson Finance": "Johnson Finance à Montpellier — un cabinet qui se distingue par une approche personnalisée et une signature affirmée.",
    "Efficience Groupe": "Efficience Groupe à Montpellier — un cabinet qui structure sa croissance autour de relations clients durables.",
    "Prestia Conseils": "Prestia Conseils à Saint-Jean-de-Védas — la précision du conseil patrimonial avec la chaleur d'un cabinet indépendant.",
    "K-Invest & Patrimoine": "K-Invest & Patrimoine à Montpellier — un cabinet qui défend une approche sélective du patrimoine.",
    "A2 Patrimoine": "A2 Patrimoine à Frontignan — un conseil patrimonial de proximité, à deux pas du littoral.",
    "Sérénité Patrimoine (Eric Bertaud)": "Cabinet Sérénité Patrimoine à Gigean — la sérénité comme promesse, pour vos clients comme pour leurs proches.",
    "Bleu Assurances et Banques": "Bleu Assurances et Banques à Gigean — une approche complète, du patrimoine à l'assurance, pour une clientèle fidèle.",
    "Cabinet Cazes Goddyn Lunel": "Cabinet Cazes Goddyn à Lunel — un cabinet historique qui accompagne plusieurs générations de clients sur le secteur.",
    "Boyer Gestion Privée": "Boyer Gestion Privée à Béziers — un cabinet qui défend le conseil indépendant haut de gamme dans l'Ouest héraultais.",
    "Cabinet Fabiani Patrimoine": "Cabinet Fabiani Patrimoine à Béziers — une signature patrimoniale qui inspire confiance dans la région.",
    "FS Courtage / Patrimonialement Votre": "FS Courtage à Notre-Dame-de-Londres — la gestion patrimoniale au cœur du Pic Saint-Loup, avec une clientèle qui vous suit.",
    "Elit'Valorys": "Elit'Valorys à Montpellier — l'élite du conseil patrimonial, comme l'indique le nom.",

    # ==== Concessions auto premium (sauf Porsche déjà fait) ====
    "Mercedes-Benz Sodira Montpellier": "Concession Mercedes-Benz à Castelnau-le-Lez — vos clients premium attendent du sur-mesure, bien au-delà de la livraison du véhicule.",
    "BMW Montpellier (Groupe GRIM)": "BMW Montpellier à Lattes — le plaisir de conduire, mais aussi celui de l'expérience client autour du véhicule.",
    "Audi DBF Montpellier": "Audi DBF à Montpellier — une clientèle exigeante qui attache autant d'importance au produit qu'à la relation.",
    "Jaguar Land Rover Montpellier": "Jaguar Land Rover Montpellier — une clientèle attachée à l'esprit britannique et à l'expérience de marque.",
    "Maserati Montpellier La Pléiade Motors": "Maserati Montpellier — une clientèle confidentielle, des modèles d'exception, des moments d'expérience qui doivent l'être tout autant.",
    "Ferrari Prestige Automobile Montpellier": "Ferrari Montpellier — une clientèle ultra-confidentielle pour qui chaque événement de marque est attendu et raconté.",
    "Lexus Montpellier (Groupe Maurin)": "Lexus Montpellier à Lattes — le luxe à la japonaise, avec une clientèle qui apprécie la discrétion et la qualité d'accueil.",
    "Volvo Espace Sud Automobiles": "Volvo Espace Sud à Mauguio — une clientèle attachée à l'esprit scandinave et à des marques qui font l'expérience client autrement.",

    # ==== Hôtellerie 5* ====
    "Domaine de Verchant Hôtel & Spa 5 etoiles": "Domaine de Verchant à Castelnau-le-Lez — votre clientèle 5 étoiles cherche des expériences mémorables, pas seulement des chambres.",
    "Hôtel Richer de Belleval 5 etoiles": "Hôtel Richer de Belleval, place de la Canourgue — l'hôtellerie d'exception en plein cœur de Montpellier, avec une clientèle qui apprécie les parenthèses rares.",
    "Plage Palace": "Plage Palace à Palavas-les-Flots — un 5 étoiles face à la mer, avec une clientèle qui cherche l'expérience exclusive plus que le simple séjour.",

    # ==== Immobilier prestige (sauf Poncet) ====
    "Acanthe Immobilier": "Acanthe Immobilier à Castelnau-le-Lez — une clientèle haut de gamme qui acquiert beaucoup plus qu'un bien.",
    "Montpellier Sotheby's International Realty": "Sotheby's International Realty à Montpellier — la signature Sotheby's auprès d'une clientèle fortunée, française et internationale.",
    "L-Immo Prestige": "L-Immo Prestige à Montferrier-sur-Lez — l'immobilier de caractère sur le secteur du Lez, avec une clientèle exigeante.",

    # ==== Promoteur ====
    "COGIM": "COGIM à Montpellier — la promotion immobilière sur le secteur depuis longtemps, avec une clientèle d'acquéreurs qui se compte en années de relation.",

    # ==== Hôtellerie classique (Cap d'Agde) ====
    "Hôtel Les Grenadines": "Hôtel Les Grenadines plage Richelieu au Cap d'Agde — l'accueil et le séjour mer sont votre quotidien.",

    # ==== Agences com / digital / web / design ====
    "Noon Collective": "Noon Collective à Montpellier — une agence créative qui sait que la cohésion d'équipe nourrit la création.",
    "OSB Communication": "OSB Communication à Montpellier — une agence qui enchaîne les campagnes et les briefs, avec une équipe qui en porte le rythme.",
    "Citrus Agence": "Citrus Agence à Castelnau-le-Lez — une agence pleine de pep's, où les bonnes idées naissent souvent en équipe.",
    "Kaneva": "Kaneva à Montpellier — une agence avec une vraie patte, et une équipe qui en construit la culture au quotidien.",
    "La Chamade": "La Chamade à Mauguio — une agence créative qui, comme le nom le dit, fait battre le cœur de ses clients.",
    "Etincelle": "Agence Etincelle à Montpellier — l'étincelle créative se cultive en équipe, autour d'expériences qui marquent.",
    "Jaune Citron": "Jaune Citron à Montpellier — une agence pétillante, où l'esprit d'équipe fait partie du produit livré.",
    "Keyrio": "Keyrio à Montpellier — une agence qui mise sur le sens et la cohésion pour livrer des campagnes fortes.",
    "Troa": "Troa à Montpellier — une agence digitale avec une vraie identité, portée par une équipe soudée.",
    "Citron Noir": "Citron Noir à Montferrier-sur-Lez — une agence avec un parti-pris fort, et une équipe qui en partage la culture.",
    "Nukium": "Nukium à Montpellier — la performance digitale est un sport collectif, vous le savez mieux que personne.",
    "Webgroup": "Webgroup à Montpellier — une agence web où l'équipe technique et créa avancent main dans la main.",
    "Studio Gazoline / Keole": "Studio Gazoline à Saint-Jean-de-Védas — une agence avec un nom qui claque, et une équipe qui carbure à fond.",
    "JumpStart Studio": "JumpStart Studio à Montpellier — un studio design où la créativité d'équipe fait toute la différence.",

    # ==== Domaines viticoles (TOP) ====
    "Mas de Daumas Gassac": "Mas de Daumas Gassac à Aniane — le « Lafite du Languedoc » selon Hugh Johnson, une signature emblématique de l'Hérault.",
    "Domaine Castan": "Domaine Castan à Cazouls-lès-Béziers — un domaine familial du Languedoc qui défend une viticulture authentique.",
    "Château Boisset": "Château Boisset en AOP Pic Saint-Loup à Valflaunès — l'élégance du Pic, dans un domaine qui en porte l'identité.",
    "Mas Bruguière": "Mas Bruguière en Pic Saint-Loup — un domaine de référence sur l'appellation, avec une signature reconnaissable entre toutes.",
    "Clos Marie": "Clos Marie à Lauret — un domaine emblématique du Pic Saint-Loup, salué bien au-delà du Languedoc.",
    "Domaine des Lauriers": "Domaine des Lauriers à Castelnau-de-Guers — la Picpoul de Pinet et les vins du littoral, une signature de l'Hérault.",
    "La Tour Penedesses": "La Tour Penedesses à Faugères — l'AOP Faugères et son terroir de schiste, dans un domaine qui en porte l'âme.",
    "Domaine Moulinier": "Domaine Moulinier à Saint-Chinian — l'appellation Saint-Chinian dans toute sa richesse, depuis un domaine familial de référence.",
    "Les Vignerons d'Ensérune": "Les Vignerons d'Ensérune à Maraussan — une cave coopérative historique, fondée en 1905, signature du vignoble biterrois.",
    "Les Caves Molière": "Les Caves Molière à Pézenas — l'esprit Molière à Pézenas, avec une cave qui porte l'identité littéraire de la ville.",
    "Mas Conscience": "Mas Conscience à Saint-Jean-de-Fos — un domaine en biodynamie sur le Terrasses du Larzac, avec un vrai parti-pris.",
    "Château de Cazeneuve": "Château de Cazeneuve à Lauret — un domaine emblématique du Pic Saint-Loup, où l'œnotourisme fait partie de l'ADN.",
    "Domaine de Mortiès": "Domaine de Mortiès à Saint-Jean-de-Cuculles — Pic Saint-Loup, biodynamie, une signature confidentielle et recherchée.",
    "Mas Champart": "Mas Champart à Saint-Chinian — un domaine de référence en Saint-Chinian Berlou, avec une renommée internationale.",
    "Château Capion": "Château Capion à Aniane — un domaine d'exception en Terrasses du Larzac, voisin de Daumas Gassac.",
    "Mas Jullien": "Mas Jullien à Jonquières — Olivier Jullien, l'un des grands noms du Languedoc, avec des vins recherchés dans le monde entier.",
    "Domaine Léon Barral": "Domaine Léon Barral à Cabrerolles — Faugères en biodynamie, une référence absolue de l'appellation et au-delà.",
    "Domaine de Cébène": "Domaine de Cébène à Faugères — Brigitte Chevalier et un domaine devenu une référence sur les schistes de Faugères.",
    "Prieuré de Saint-Jean de Bébian": "Prieuré de Saint-Jean de Bébian à Pézenas — un domaine historique du Languedoc, l'un des pionniers de la qualité dans la région.",
    "Mas Coutelou": "Mas Coutelou à Puimisson — Jeff Coutelou, vins natures et identité forte, une signature suivie partout en France et au-delà.",
    "Domaine Rimbert": "Domaine Rimbert à Berlou — l'âme des schistes de Saint-Chinian Berlou, avec des cuvées qui ont fait connaître le terroir.",
    "Domaine de l'Aiguelière": "Domaine de l'Aiguelière à Montpeyroux — un domaine de référence en Terrasses du Larzac, l'une des appellations qui montent.",
    "Château de Granoupiac": "Château de Granoupiac à Saint-André-de-Sangonis — un domaine au cœur du Cœur d'Hérault, accueillant et tourné vers ses visiteurs.",
    "Château La Liquière": "Château La Liquière à Cabrerolles — l'un des plus anciens domaines de Faugères, avec une famille qui en perpétue l'identité.",
    "Mas Laval": "Mas Laval à Aniane — Terrasses du Larzac, un domaine qui s'est imposé parmi les belles signatures du secteur d'Aniane.",
    "Château de Lascaux": "Château de Lascaux à Vacquières — un domaine de référence en Pic Saint-Loup, avec une production saluée bien au-delà du Languedoc.",

    # ==== Traiteurs (sauf Cabiron déjà fait) ====
    "Madame Pari": "Madame Pari à Castelnau-le-Lez — un univers traiteur soigné, où la table fait partie intégrante de l'événement.",
    "Andrieux Traiteur": "Andrieux Traiteur à Saint-Jean-de-Védas — un savoir-faire de traiteur qui accompagne mariages et événements pros sur tout l'Hérault.",
    "Traiteur des Garrigues": "Traiteur des Garrigues à Saint-Jean-de-Védas — un univers gourmand inspiré du Sud, qui met le terroir dans l'assiette.",
    "L'Atelier Nomade": "L'Atelier Nomade à Ceyras — un traiteur qui se déplace au gré des événements, avec une vraie identité.",
    "Brasero Gourmand": "Brasero Gourmand à Montpellier — un univers brasero qui change des cocktails classiques, avec une signature forte.",
    "Camille Réceptions": "Camille Réceptions à Clermont-l'Hérault — un traiteur réception qui accompagne les beaux événements de l'Ouest héraultais.",
    "Parguel Traiteur": "Parguel Traiteur boulevard Vieussens — une signature historique du traiteur événementiel à Montpellier.",
    "Amis Traiteur": "Amis Traiteur à Castries — un traiteur convivial, comme le nom l'indique, ancré sur le secteur.",
    "Frais'Ro Traiteur": "Frais'Ro Traiteur à Montpellier — la fraîcheur des produits comme signature, pour des événements qui sortent du cadre.",
    "Grain de Sel Traiteur": "Grain de Sel Traiteur à Thézan-lès-Béziers — un traiteur biterrois qui amène le grain de sel des belles tables.",
    "Les Savouries Traiteur": "Les Savouries Traiteur à Béziers — un traiteur biterrois qui mise sur la créativité culinaire pour ses clients.",
    "Domaine de Pradines Traiteur": "Domaine de Pradines à Béziers — un domaine traiteur qui propose lieu et prestation dans un même esprit.",
    "Amélie Traiteur": "Amélie Traiteur à Mauguio — un traiteur reconnu sur le secteur, avec une vraie identité de marque.",
    "Traiteur Trémeau": "Traiteur Trémeau à Montpellier — un savoir-faire de traiteur événementiel ancré sur la métropole.",
    "AJM Traiteur": "AJM Traiteur à Montpellier — un traiteur événementiel avec une vraie écoute pour des événements sur-mesure.",
    "Carrié Traiteur": "Carrié Traiteur à Sète — un traiteur sétois qui accompagne mariages et beaux événements sur le Bassin de Thau.",
    "L'Atelier de Nicolas": "L'Atelier de Nicolas à Villeneuve-lès-Béziers — un traiteur biterrois qui défend une cuisine soignée pour ses événements.",
    "Le Festin du Roi Traiteur": "Le Festin du Roi place Castellane — un traiteur royal au cœur de Montpellier, avec une signature qui claque.",
    "Braise Cave & Table": "Braise Cave & Table à Montpellier — l'univers de la braise et de la cave, une vraie identité dans le paysage traiteur.",

    # ==== Wedding planners (sauf Manava) ====
    "Histoire d'Ange": "Histoire d'Ange à Clermont-l'Hérault — un univers wedding raffiné, où la magie du lieu fait toute la différence.",
    "Souffles de Fées": "Souffles de Fées à Montpellier — un univers wedding poétique, où chaque cadre choisi raconte une histoire.",
    "Glamour Events": "Glamour Events à Montpellier — un univers événementiel haut de gamme, où le cadre fait partie du contrat avec les mariés.",
    "Elikya Events": "Elikya Events à Saint-Georges-d'Orques — un univers wedding élégant, qui sait qu'un beau lieu vaut tous les discours.",
    "HH Créations": "HH Créations à Montpellier — wedding planner avec une vraie identité, où le choix du lieu pèse souvent dans la décision des mariés.",
    "C'est le Grand Jour": "C'est le Grand Jour à Montpellier — un nom qui dit tout : le grand jour mérite un cadre à la hauteur.",
    "Boogie Event": "Boogie Event à Baillargues — un univers wedding qui a sa patte, et une clientèle qui cherche des cadres originaux.",
    "Ophélie Torres Wedding Planner": "Ophélie Torres à Montpellier — une signature wedding qui mise sur l'élégance et la justesse des lieux.",
    "Bride Squad": "Bride Squad à Montpellier — un univers wedding moderne, où les couples cherchent du cadre, du sur-mesure et de l'expérience.",
}


def get_top_hook(nom: str):
    return TOP_HOOKS.get(nom)


# ---------- Hook sectoriel template ----------
def get_template_hook(secteur: str, ville: str, nom: str) -> str:
    s = secteur.strip()
    v = ville.strip()
    if s == "Avocats":
        return f"Cabinet d'avocats à {v} — un quotidien dense en dossiers et en clients."
    if s == "Notaire":
        return f"Étude notariale à {v}, des journées chargées entre signatures et dossiers."
    if s == "BTP":
        return f"Entreprise du BTP basée à {v}, des équipes qui mettent les mains dedans toute l'année."
    if s == "Architecte":
        return f"Cabinet d'architecture à {v}, des projets qui demandent autant de rigueur que de créativité."
    if s == "Architecte intérieur":
        return f"Agence d'architecture d'intérieur à {v}, des projets exigeants qui mobilisent l'équipe sur la durée."
    if s == "Bureau d'études":
        return f"Bureau d'études basé à {v}, des projets techniques qui mobilisent l'équipe sur la durée."
    if s == "Expert-comptable":
        return f"Cabinet d'expertise comptable à {v} — vos équipes connaissent bien les pics de saison."
    if s in {"Agence com", "Agence digitale", "Agence web", "Agence design"}:
        return f"Agence créative à {v}, un univers où l'équipe et la cohésion font la différence."
    if s == "Agence événementielle":
        return f"Agence événementielle à {v} — vous savez mieux que personne ce qu'un cadre fort apporte à un événement."
    if s == "Immobilier":
        return f"Agence immobilière à {v}, une équipe qui jongle entre prospection, visites et signatures."
    if s == "Immobilier prestige":
        return f"Agence immobilière prestige à {v}, une clientèle qui acquiert plus qu'un bien."
    if s == "Promoteur immobilier":
        return f"Promotion immobilière à {v}, des projets longs qui mobilisent vos équipes sur la durée."
    if s == "EnR":
        return f"Spécialiste EnR à {v}, un secteur qui pousse fort et demande des équipes engagées."
    if s == "Climatisation":
        return f"Spécialiste climatisation à {v}, une activité où les équipes sont mobilisées toute la saison."
    if s == "Industrie":
        return f"Site industriel à {v}, des équipes solides au cœur d'un savoir-faire technique."
    if s == "Logistique":
        return f"Activité logistique basée à {v}, des équipes mobilisées toute la semaine sur le terrain."
    if s == "Restauration":
        if "traiteur" in nom.lower():
            return f"Traiteur à {v} — vous savez mieux que personne ce qu'une belle table apporte à un événement."
        return f"Restaurant à {v} — vous savez ce que cohésion et expérience signifient pour vos équipes."
    if s == "Signalétique":
        return f"Atelier signalétique à {v}, des équipes qui jonglent entre production et délais."
    if s == "Propreté":
        return f"Société de services de propreté à {v}, des équipes terrain qu'il est rare de pouvoir réunir."
    if s == "Sécurité":
        return f"Société de sécurité à {v}, des équipes terrain qu'il est rare de pouvoir réunir."
    if s == "Wedding planner":
        return "Wedding planner sur l'Hérault — une activité où la magie des lieux fait tout."
    if s in {"Cabinet recrutement", "Cabinet conseil RH"}:
        return f"Cabinet RH à {v}, un quotidien de rencontres et de placements."
    if s == "Cabinet conseil":
        return f"Cabinet de conseil à {v}, des missions exigeantes qui demandent une équipe en forme."
    if s in {"Courtage assurance", "Courtage crédit", "Courtage énergie", "Courtage travaux"}:
        return f"Cabinet de courtage à {v} — vos équipes commerciales tiennent la cadence."
    if s in {"Hôtellerie", "Hôtellerie 5 étoiles", "Hôtellerie 5 etoiles"}:
        return f"Établissement hôtelier à {v}, l'accueil et l'expérience sont votre quotidien."
    if s in {"Éditeur logiciel", "Éditeur logiciel / ESN"}:
        return f"Éditeur logiciel à {v}, des équipes tech qui livrent dans la durée."
    if s == "Négoce":
        return f"Activité de négoce basée à {v}, des équipes mobilisées sur le terrain et au bureau."
    if s == "Agence voyages":
        return f"Agence de voyages à {v}, vous savez mieux que personne ce qu'un beau cadre apporte à un voyage."
    if s == "Viticulture":
        return f"Domaine viticole à {v}, une activité où l'identité du lieu fait tout."
    if s == "Traiteur":
        return f"Maison de traiteur à {v} — vous savez mieux que personne ce qu'une belle table apporte à un événement."
    return f"Activité basée à {v}, des équipes qui portent la maison au quotidien."


# ---------- Yacht intro variations ----------
YACHT_INTROS = [
    "Je vous écris depuis Harmonie Yacht, basé au port de Carnon ({DIST} de {VILLE}), où nous proposons la privatisation de notre yacht pour des sorties en petit comité (jusqu'à 10 personnes).",
    "Côté Carnon, nous proposons depuis Harmonie Yacht la privatisation de notre yacht — sorties en petit comité, jusqu'à 10 personnes, {DIST} de {VILLE}.",
    "À {DIST_NUM} de chez vous, nous proposons depuis Harmonie Yacht (port de Carnon) la privatisation de notre yacht pour des sorties en petit comité — jusqu'à 10 personnes.",
    "Je vous écris depuis Harmonie Yacht, au port de Carnon, {DIST} de {VILLE} : on propose la privatisation de notre yacht pour des sorties en petit comité (jusqu'à 10 personnes).",
]


def _de_ville(ville: str) -> str:
    """Retourne 'de Ville', 'd'Ville', ou 'du Ville' selon voyelle / cas particulier."""
    # Cas particuliers
    if ville == "Cap d'Agde":
        return "du Cap d'Agde"
    if ville == "Le Crès":
        return "du Crès"
    if ville and ville[0].lower() in "aeiouéèêâîôûh":
        return f"d'{ville}"
    return f"de {ville}"


def _a_ville(ville: str) -> str:
    """Retourne 'à Ville' ou 'au Ville' selon cas."""
    if ville == "Le Crès":
        return "au Crès"
    if ville == "Cap d'Agde":
        return "au Cap d'Agde"
    return f"à {ville}"


def make_yacht_intro(idx: int, ville: str, dist: str) -> str:
    tpl = YACHT_INTROS[idx % len(YACHT_INTROS)]
    # dist_num : sans "à " devant
    dist_num = dist.replace("à ", "")
    de_ville = _de_ville(ville)
    # Adapter les templates : remplacer "de {VILLE}" par {DE_VILLE}
    out = tpl.format(DIST=dist, VILLE=ville, DIST_NUM=dist_num)
    # Corriger "de Aniane" -> "d'Aniane", "à 45 min de Aniane" -> "à 45 min d'Aniane"
    out = out.replace(f"de {ville}", de_ville)
    out = out.replace(f"{dist} de {ville}", f"{dist} {de_ville}")
    return out


# ---------- Angle usage ----------
def get_angle(segment: str, secteur: str) -> str:
    if segment == "A":
        # type entreprise selon secteur
        if secteur == "CGP":
            return ("C'est typiquement utilisé par les cabinets de gestion privée pour fidéliser "
                    "leurs clients les plus engagés — soirée patrimoniale en mer, événement client "
                    "exclusif, anniversaire de relation.")
        if secteur == "Concession auto premium":
            return ("C'est typiquement utilisé par les concessions premium pour fidéliser leurs "
                    "propriétaires — lancement de modèle, club privé, événement anniversaire client.")
        if secteur in {"Hôtellerie 5 étoiles", "Hôtellerie 5 etoiles"}:
            return ("C'est un format que les belles maisons utilisent en complément de leur offre — "
                    "expérience client VIP, lancement de saison, partenariat exclusif.")
        if secteur in {"Immobilier prestige"}:
            return ("C'est un format que les agences haut de gamme utilisent pour les remises de "
                    "clés VIP, les cocktails post-signature ou simplement pour fidéliser leurs "
                    "acquéreurs prestigieux.")
        if secteur == "Promoteur immobilier":
            return ("C'est un format utilisé par les promoteurs pour les remises de clés VIP, "
                    "les lancements de programmes ou les événements prescripteurs.")
        return ("C'est typiquement utilisé pour fidéliser vos clients les plus engagés — "
                "soirée privée, événement de marque, anniversaire client.")
    if segment == "B":
        return ("C'est typiquement utilisé pour souder un comité de direction, marquer la fin "
                "d'un gros projet ou récompenser une belle année.")
    if segment == "C":
        # partenariat
        if secteur == "Wedding planner":
            return ("Plutôt qu'une prestation, je voulais vous présenter une **collaboration** : "
                    "vos couples qui cherchent un format intimiste hors lieu de réception classique, "
                    "votre prestation, notre logistique mer. Commission ou co-prestation à définir ensemble.")
        if secteur == "Agence événementielle":
            return ("Plutôt qu'une prestation, je voulais vous présenter une **collaboration** : "
                    "vos clients qui cherchent un format intimiste hors lieu habituel, votre orchestration, "
                    "notre logistique mer. Commission ou co-prestation à définir ensemble.")
        if secteur in {"Hôtellerie", "Hôtellerie 5 étoiles", "Hôtellerie 5 etoiles"}:
            return ("Plutôt qu'une prestation, je voulais vous présenter une **collaboration** : "
                    "vos clients qui cherchent une parenthèse mer, votre accueil, notre logistique. "
                    "Commission ou co-prestation à définir ensemble.")
        # Traiteur / restau-traiteur
        return ("Plutôt qu'une prestation, je voulais vous présenter une **collaboration** : "
                "vos clients qui cherchent un format intimiste hors de votre lieu habituel, "
                "votre prestation, notre logistique mer. Commission ou co-prestation à définir ensemble.")
    if segment == "D":
        return ("Une idée qu'on développe avec quelques domaines : un format **mer + dégustation** "
                "pour vos visiteurs premium ou vos importateurs — yacht l'après-midi, dégustation "
                "au domaine en fin de journée.")
    # E
    return ("Deux usages typiques : séminaire d'équipe pour souffler après une saison chargée, "
            "ou événement client privé pour fidéliser vos clients clés.")


# ---------- Objet ----------
def get_objet(segment: str, secteur: str, ville: str, nom: str) -> str:
    if segment == "A":
        if secteur == "CGP":
            return f"Une expérience pour vos clients patrimoine"
        if secteur == "Concession auto premium":
            return f"Une expérience pour vos clients propriétaires"
        if secteur in {"Hôtellerie 5 étoiles", "Hôtellerie 5 etoiles"}:
            return f"Une expérience à proposer à vos clients 5 étoiles"
        if secteur == "Immobilier prestige":
            return f"Une expérience pour votre clientèle prestige"
        if secteur == "Promoteur immobilier":
            return f"Une expérience pour vos acquéreurs"
        return f"Un cadeau client à {ville}"
    if segment == "B":
        return f"Idée séminaire d'équipe à 15 min de Montpellier"
    if segment == "C":
        if secteur == "Wedding planner":
            return "Une carte yacht à ajouter à votre offre wedding ?"
        if secteur == "Agence événementielle":
            return "Une carte yacht à ajouter à votre offre événementielle ?"
        if secteur in {"Hôtellerie", "Hôtellerie 5 étoiles", "Hôtellerie 5 etoiles"}:
            return "Une collaboration possible côté mer ?"
        return "Une collaboration possible côté mer ?"
    if segment == "D":
        return "Vos visiteurs domaine, embarqués depuis Carnon ?"
    return f"Un cadre différent pour votre équipe ?"


# ---------- CTA + ce qui est envoyé ----------
def get_cta(segment: str) -> tuple:
    if segment == "C":
        return ("vous voulez en savoir plus", "notre offre partenaire (commissions, modalités)")
    if segment == "D":
        return ("vous voulez recevoir notre formule", "notre proposition (tarifs et programmes)")
    # A, B, E
    return ("ça vous parle", "notre formule détaillée (tarifs, créneaux, exemples de programmes)")


# ---------- Génération du mail ----------
def build_mail(idx: int, lead: dict) -> tuple:
    """Retourne (subject, body, prenom_extrait_or_empty)."""
    nom = lead["nom"]
    secteur = lead["secteur"]
    email = lead["email"]
    ville = lead["ville"] or "Montpellier"
    dist = get_distance(ville)
    salut = get_salut(email)
    segment = get_segment(secteur, nom)
    # Hook
    top = get_top_hook(nom)
    if top:
        hook = top
    else:
        hook = get_template_hook(secteur, ville, nom)
    yacht_intro = make_yacht_intro(idx, ville, dist)
    angle = get_angle(segment, secteur)
    cta_phrase, ce_qui_envoye = get_cta(segment)
    objet = get_objet(segment, secteur, ville, nom)

    # Adapter "à 15 min de Montpellier" dans l'objet B
    if segment == "B":
        objet = f"Idée séminaire d'équipe {dist} {_de_ville(ville)}"

    # Compose body
    body = (
        f"{salut}\n\n"
        f"{hook}\n\n"
        f"{yacht_intro}\n\n"
        f"{angle}\n\n"
        f"L'idée du mail n'est pas de vous vendre quoi que ce soit aujourd'hui, juste de "
        f"me présenter. Si {cta_phrase}, répondez-moi simplement « oui » et je vous envoie "
        f"{ce_qui_envoye} sous 24h.\n\n"
        f"Excellente journée,\n"
        f"Robin & Ludivine — Harmonie Yacht\n"
        f"Port de Carnon\n\n"
        f"PS : si ça ne vous concerne pas, dites-le-moi et je vous laisse tranquille."
    )
    # Corrections grammaticales fines
    body = body.replace("à Le Crès", "au Crès")
    body = body.replace("à Cap d'Agde", "au Cap d'Agde")
    objet = objet.replace("à Le Crès", "au Crès").replace("à Cap d'Agde", "au Cap d'Agde")
    # Extraire prenom
    prenom = ""
    if salut.startswith("Bonjour ") and salut != "Bonjour,":
        prenom = salut[len("Bonjour "):].rstrip(",").strip()
    return objet, body, prenom, segment


# ---------- Main ----------
def main():
    rows = []
    with open(SRC, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    skipped_no_email = []
    counts = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}
    web_searches = 0  # nb de hooks "TOP" appliqués

    txt_chunks = []
    csv_rows = [["Email", "Prenom", "Entreprise", "Segment", "Subject", "Body",
                 "Date_envoi", "Ouvert", "Clique", "Repondu", "Statut",
                 "Date_M2", "Date_M3", "Notes"]]

    lead_idx = 11  # on démarre à #11
    for r in rows:
        nom = r["nom"].strip()
        if nom in ALREADY_DONE:
            continue
        email = (r.get("email") or "").strip()
        secteur = (r.get("secteur") or "").strip()
        ville = (r.get("ville") or "").strip() or "Montpellier"
        if not email:
            skipped_no_email.append(f"{nom} ({secteur}, {ville})")
            continue

        objet, body, prenom, segment = build_mail(lead_idx, {
            "nom": nom, "secteur": secteur, "email": email, "ville": ville,
        })
        counts[segment] += 1
        if get_top_hook(nom):
            web_searches += 1

        seg_lib = SEG_LIBELLE[segment]
        chunk = (
            "================================================================================\n"
            f"LEAD #{lead_idx} — {nom}  (Segment {segment} : {seg_lib})\n"
            "================================================================================\n"
            f"À : {email}\n"
            f"Objet : {objet}\n\n"
            f"{body}\n\n"
        )
        txt_chunks.append(chunk)

        csv_rows.append([
            email, prenom, nom, segment, objet, body,
            "", "", "", "", "", "", "", "",
        ])
        lead_idx += 1

    # Write TXT
    header = (
        "# Mails de prospection - Phase 2 (273 mails)\n"
        "# Harmonie Yacht - Carnon\n"
        "# Robin & Ludivine\n\n"
    )
    OUT_TXT.write_text(header + "\n".join(txt_chunks), encoding="utf-8")

    # Write CSV
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        for row in csv_rows:
            w.writerow(row)

    total = sum(counts.values())
    print(f"TOTAL : {total} mails générés")
    print(f"- Segment A : {counts['A']}")
    print(f"- Segment B : {counts['B']}")
    print(f"- Segment C : {counts['C']}")
    print(f"- Segment D : {counts['D']}")
    print(f"- Segment E : {counts['E']}")
    print(f"Skipped (no email) : {len(skipped_no_email)}")
    print(f"WebSearch effectués (TOP leads) : {web_searches}")
    if skipped_no_email:
        print("\n--- Leads skipped (no email) ---")
        for s in skipped_no_email:
            print(f"  - {s}")


if __name__ == "__main__":
    main()
