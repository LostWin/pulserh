# Seuils de gravité du risque
RISK_THRESHOLD_HIGH = 70
RISK_THRESHOLD_MEDIUM = 45

def explain_risk_score(factors: list[dict]) -> tuple[list[dict], str, str]:
    """Interprète le score de risque pour fournir une recommandation."""
    top_factors = sorted(factors, key=lambda item: item["value"], reverse=True)[:3]
    
    if not top_factors:
        return [], "green", "Aucun risque identifié."
        
    score = round(sum(item["value"] for item in top_factors) / len(top_factors))
    level = "red" if score >= RISK_THRESHOLD_HIGH else "orange" if score >= RISK_THRESHOLD_MEDIUM else "green"
    
    recommendations = {
        "Charge de travail": "Rééquilibrer la charge, clarifier les priorités et revoir les échéances des projets actifs.",
        "Assiduité": "Prévoir un point de suivi et analyser les causes des absences récentes avec le manager.",
        "Formation obligatoire": "Débloquer rapidement les formations obligatoires et lever les freins d'accès.",
        "Engagement déclaré": "Planifier un échange de proximité et mettre en place un plan d'accompagnement ciblé.",
        "Reconnaissance / progression": "Proposer un feedback structuré, une perspective d'évolution et un plan de développement."
    }
    
    recommendation = recommendations.get(top_factors[0]["label"], "Prévoir un entretien ciblé avec le collaborateur.")
    
    return top_factors, level, recommendation
