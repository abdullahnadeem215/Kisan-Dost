"""
Google Gemini Vision Multimodal Client for Kisan Dost.
Provides plant pathology & pest identification with strict agricultural domain guardrails.
"""
import json
import logging
from typing import Optional, Dict, Any
import httpx
from config.settings import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Client for interacting with Google Gemini Vision Multimodal API.
    Enforces strict farming-only guardrails: rejects non-agricultural pictures.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key

    def diagnose_crop_image(
        self,
        image_base64: str,
        mime_type: str = "image/jpeg",
        crop_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submits plant/crop photograph to Gemini Vision with agricultural safety prompt.
        Returns parsed diagnosis or refusal dictionary.
        """
        if not self.api_key:
            return {
                "is_farming_related": True,
                "error": "GEMINI_API_KEY_NOT_CONFIGURED",
                "fallback": True
            }

        prompt = f"""
You are the Chief Plant Pathologist and Agronomy Specialist for Kisan Dost (Pakistan).
Examine this uploaded photograph to diagnose crop disease, nutritional deficiency, or pest infestation.

CRITICAL FIRST STEP - AGRICULTURAL RELEVANCE GUARDRAIL:
Determine if this image is genuinely related to agriculture, farming, crops, leaves, plant stems, roots, fields, soil, or agricultural pests/insects.
- IF IT IS NOT A FARMING/CROP/PLANT IMAGE (e.g. human face, medical condition, car, pet animal, furniture, document, room, screenshot):
  Set "is_farming_related": false.
  Set "refusal_reason_roman_urdu": "Yeh tasveer kisi fasal ya paudhay ki nahi hai. Kisan Dost sirf zaraat aur kheti baari se mutalliq tasveeron ki tashkhees karta hai. Barah-e-karam fasal ke pattay ya mutasira hissay ki saaf tasveer upload karein."
  Set "refusal_reason_urdu": "یہ تصویر کسی فصل یا پودے کی نہیں ہے۔ کسان دوست صرف زراعت اور کھیتی باڑی سے متعلق پودوں اور پتوں کی تشخیص کرتا ہے۔ برائے مہربانی فصل کے پتے یا کیڑے کی تصویر اپلوڈ کریں۔"
  Set "refusal_reason_en": "This image is not related to farming or crops. Kisan Dost only inspects agricultural crops, plant leaves, and farm pests. Please upload a clear photo of an affected leaf or plant."
  Do NOT attempt to diagnose non-farming items.

- IF IT IS A FARMING/CROP/PLANT IMAGE:
  Set "is_farming_related": true.
  Inspect symptoms on the crop {f'(Farmer indicated crop: {crop_hint})' if crop_hint else ''}.
  Chemical control MUST strictly adhere to the Department of Plant Protection (DPP) Pakistan official pesticide registry (e.g. Nativo 75 WG @ 65g/acre, Pyriproxyfen 10.8 EC @ 500ml/acre).
  Never hallucinate unregistered chemical dosages.

Return ONLY valid JSON:
{{
  "is_farming_related": true,
  "refusal_reason_roman_urdu": null,
  "refusal_reason_urdu": null,
  "refusal_reason_en": null,
  "crop_name": "Crop Name",
  "disease_name": "Disease/Pest Name",
  "causal_agent": "Pathogen/Pest Type",
  "match_confidence": 0.94,
  "symptoms": ["Symptom description 1", "Symptom description 2"],
  "favorable_conditions": "Favorable environmental conditions",
  "preventative_measures": ["Preventative cultural practice 1"],
  "organic_control": "Organic remedy or bio-control",
  "chemical_control": "DPP registered chemical with acre dosage",
  "dosage_per_acre": "Dosage per acre",
  "diagnostic_summary_roman_urdu": "Advice in Roman Urdu",
  "diagnostic_summary_urdu": "Advice in Urdu",
  "diagnostic_summary_en": "Advice in English"
}}
"""

        models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash"]
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": image_base64
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "responseMimeType": "application/json"
                }
            }

            try:
                with httpx.Client(timeout=30.0) as client:
                    resp = client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        raw_text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        if raw_text:
                            return json.loads(raw_text)
                    else:
                        logger.warning(f"Gemini {model} returned status {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.error(f"Error calling Gemini {model}: {e}")

        return {
            "is_farming_related": True,
            "error": "GEMINI_INFERENCE_FAILED",
            "fallback": True
        }
