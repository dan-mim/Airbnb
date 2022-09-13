      Prérequis: 
          -Il faut qu'un document 'tab_lat_long.csv' soit dans le mêle répertoire que le code.
      Ce code a pour objectif de récupérr toutes les localisations (capacité et prix), des Airbnb en Ile de France.
      Pour cela il s'appuie sur le scraping de données en utilisant Selenium et Requests_html.
      Le code fonctionne en 6 étapes:
    1) Au préalable la carte de l'IDF est découpée en un certain nombre de carrés geographiques
    2) Les recherches se font geographiquement carré par carré: je parcours la liste des carrés et ils sont analysés  séparement comme requètes geographiques sur Airbnb
    3) Pour chaque requète géographique, je filtre par prix pas à pas car la limite d'affichage de Airbnb est de 300 logements pa recherche donc on ne veut pas dépasser cette limite.
    4) Une fois qu'on a fait une requète géographique + une requète par prix (via filtrage), on enrregistre l'url de la page en cours et on ouvre virtuellement cette url avec requests_html (on crée une 'session')
    On passe alors à la page suivant de la meme requete (georgpahie + filtrage prix mais page 2, puis 3, puis ... 15)
    5) Une fois la session ouverte, je scrape les données qui m'interessent. 
    remarque: avec requests_htm je n'ai pas beoin d'attendre le chargement de la page je récupère directement depuis le réseau.
    6) Je concatène les résultats page par page, puis plage de prix par plage de prix, puis carré par carré grâce à la fonction 'concat_all()'
      