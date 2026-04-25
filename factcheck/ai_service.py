import json
import urllib.request
import urllib.error
from django.conf import settings


SYSTEM_PROMPT = """Tu es un expert en vérification des faits (fact-checking) spécialisé dans le contexte algérien et maghrébin.
Ton rôle est d'analyser des textes ou affirmations et de déterminer leur crédibilité.

Réponds TOUJOURS en JSON valide avec cette structure exacte:
{
  "verdict": "true" | "false" | "misleading" | "partial" | "unverifiable",
  "confidence_score": 0.0-1.0,
  "explanation": "Explication détaillée en français (2-4 phrases)",
  "key_claims": "Affirmations clés identifiées (séparées par des points-virgules)",
  "red_flags": "Signaux d'alerte détectés (séparés par des points-virgules, vide si aucun)",
  "sources_suggested": "Sources recommandées pour vérifier (séparées par des points-virgules)"
}

Critères d'évaluation:
- true: Information vérifiée et exacte
- false: Information clairement fausse ou trompeuse
- misleading: Information partiellement vraie mais présentée de façon trompeuse
- partial: Partiellement vrai, nécessite des nuances
- unverifiable: Impossible à vérifier avec les données disponibles

Sois objectif, factuel et basé sur des preuves."""


def analyze_with_claude(text: str, url: str = '') -> dict:
    """Call Claude API to fact-check the given text."""
    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')

    if not api_key:
        # Demo mode: return a mock response
        return _demo_response(text)

    user_content = f"Analyse cette information pour vérification des faits:\n\n"
    if url:
        user_content += f"URL: {url}\n\n"
    user_content += f"Texte:\n{text}"

    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_content}]
    }

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            raw = data['content'][0]['text']
            # Strip markdown code fences if present
            raw = raw.strip()
            if raw.startswith('```'):
                raw = raw.split('```')[1]
                if raw.startswith('json'):
                    raw = raw[4:]
            result = json.loads(raw.strip())
            return result
    except urllib.error.URLError as e:
        return {'error': f"Erreur réseau: {str(e)}"}
    except (json.JSONDecodeError, KeyError) as e:
        return {'error': f"Erreur de parsing: {str(e)}"}
    except Exception as e:
        return {'error': f"Erreur inattendue: {str(e)}"}


def _demo_response(text: str) -> dict:
    """Return a demo response when no API key is configured."""
    text_lower = text.lower()
    # Simple heuristic for demo
    if any(w in text_lower for w in ['fake', 'faux', 'mensonge', 'rumeur']):
        verdict = 'false'
        confidence = 0.72
        explanation = "DEMO: Cette affirmation contient plusieurs indicateurs de désinformation. Les termes utilisés et la structure du message correspondent à des patterns de fausses informations souvent circulant sur les réseaux sociaux."
    elif any(w in text_lower for w in ['officiel', 'gouvernement', 'ministère', 'aps']):
        verdict = 'true'
        confidence = 0.81
        explanation = "DEMO: Cette information semble provenir d'une source officielle. La formulation est cohérente avec les communications gouvernementales algériennes."
    else:
        verdict = 'unverifiable'
        confidence = 0.55
        explanation = "DEMO: Cette affirmation ne peut pas être vérifiée sans sources complémentaires. Il est recommandé de consulter des sources officielles avant de partager cette information."

    return {
        "verdict": verdict,
        "confidence_score": confidence,
        "explanation": f"[MODE DÉMO — Configurez ANTHROPIC_API_KEY pour l'analyse réelle]\n{explanation}",
        "key_claims": "Affirmation principale identifiée; Contexte temporel présent; Acteurs mentionnés",
        "red_flags": "Source non précisée; Langage émotionnel détecté" if verdict == 'false' else "",
        "sources_suggested": "APS (Algérie Presse Service); El Watan; TSA Algérie; Radio Algérie Internationale"
    }
