def generate_meeting_analysis_prompts(text_input, language="FR"):
    system_prompt = """DIRECTIVES D'ANALYSE AUDIO/VIDÉO:
    
    TON RÔLE:
    Tu es un expert en analyse de contenus audiovisuels professionnels.
    
    FORMAT DE RÉPONSE:
    1. Résumé principal (5 lignes maximum)
    2. Points essentiels par section
    3. Éléments factuels et mesurables
    4. Plan d'action concret
    
    RÈGLES DE STYLE:
    - Phrases courtes et précises (max 15 mots)
    - Verbes au présent uniquement
    - Vocabulaire professionnel
    - Format structuré avec puces
    - Données chiffrées en numériques
    
    INTERDICTIONS:
    - Pas de suppositions
    - Pas de conditionnel
    - Pas de familiarités
    - Pas d'interprétations personnelles
    - Pas de métadiscours
    - Pas d'interrogations
    - Pas de recommandations
    - Pas de formules de politesse
    - Pas d'avis subjectifs
    
    FORMATAGE:
    - Montants: XXX €
    - Pourcentages: XX%
    - Durées: HH:MM:SS
    - Listes: puces concises
    """

    base_prompts = {
        "compte_rendu": {
            "description": "Compte-rendu détaillé",
            "sections": [
                "RÉSUMÉ PRINCIPAL",
                "ORDRE DU JOUR",
                "DISCUSSIONS",
                "DÉCISIONS",
                "ACTIONS",
            ],
            "prompt": f"{system_prompt}\n\nGénération du compte-rendu:\n{text_input}",
        },
        "qui_dit_quoi": {
            "description": "Attribution des propos",
            "sections": [
                "INTERVENANTS",
                "CITATIONS",
                "PROPOSITIONS",
                "ENGAGEMENTS",
                "DÉSACCORDS",
            ],
            "prompt": f"{system_prompt}\n\nAnalyse des interventions par participant:\n{text_input}",
        },
        "questions_reponses": {
            "description": "Questions et réponses",
            "sections": [
                "QUESTIONS POSÉES",
                "RÉPONSES APPORTÉES",
                "POINTS EN SUSPENS",
                "CLARIFICATIONS",
                "SUIVIS",
            ],
            "prompt": f"{system_prompt}\n\nExtraction des questions et réponses:\n{text_input}",
        },
        "emotions": {
            "description": "Analyse émotionnelle",
            "sections": [
                "CLIMAT GÉNÉRAL",
                "TENSIONS",
                "CONSENSUS",
                "ENGAGEMENT",
                "DYNAMIQUE",
            ],
            "prompt": f"{system_prompt}\n\nAnalyse du climat émotionnel:\n{text_input}",
        },
        "statistiques": {
            "description": "Données statistiques",
            "sections": [
                "CHIFFRES CLÉS",
                "RATIOS",
                "ÉVOLUTIONS",
                "PROJECTIONS",
                "BENCHMARKS",
            ],
            "prompt": f"{system_prompt}\n\nExtraction des statistiques:\n{text_input}",
        },
        "mindmap": {
            "description": "Carte mentale",
            "sections": [
                "THÈME CENTRAL",
                "BRANCHES PRINCIPALES",
                "SOUS-THÈMES",
                "CONNEXIONS",
                "HIÉRARCHIE",
            ],
            "prompt": f"{system_prompt}\n\nCréation d'une carte mentale:\n{text_input}",
        },
        "points_focus": {
            "description": "Points d'attention majeurs",
            "sections": ["PRIORITÉS", "URGENCES", "IMPACTS", "CRITICITÉS", "VIGILANCE"],
            "prompt": f"{system_prompt}\n\nIdentification des points critiques:\n{text_input}",
        },
    }

    return base_prompts
