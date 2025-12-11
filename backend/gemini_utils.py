import os
import vertexai
from vertexai.generative_models import GenerativeModel
import logging

logger = logging.getLogger(__name__)

PROJECT_ID = os.getenv("GCP_PROJECT")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")

_INITIALIZED = False

def _init_vertex():
    print("Initializing Vertex AI...")
    global _INITIALIZED
    if not _INITIALIZED:
        if not PROJECT_ID:
            logger.warning("GCP_PROJECT not set, skipping Vertex AI init. Gemini features will fail if not authenticated via ADC with project quota.")
            print("GCP_PROJECT not set, skipping Vertex AI init. Gemini features will fail if not authenticated via ADC with project quota.")
        try:
            vertexai.init(project=PROJECT_ID, location=LOCATION)
            _INITIALIZED = True
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            print(f"Failed to initialize Vertex AI: {e}")

def get_food_triggers(food_label: str, image_bytes: bytes) -> str:
    """
    Analyzes the food item and image using Gemini to identify potential dietary triggers.
    """
    _init_vertex()

    try:
        model = GenerativeModel("gemini-2.5-flash-lite")
        print("Gemini model initialized.")

        prompt = f"""
        You are a nutritionist assistant. The user is about to eat a meal identified as "{food_label}".
        
        List common dietary triggers associated with this food (e.g., Gluten, Lactose, Nuts, Shellfish, High Sugar, High Sodium, etc.).
        If there are no common triggers, say "None".
        
        Format the output as a simple comma-separated list of triggers. Do not include any other text or markdown.
        Example Output: Gluten, Lactose
        """

        responses = model.generate_content(
            [prompt],
            generation_config={
                "max_output_tokens": 256,
                "temperature": 0.4,
                "top_p": 1.0,
                "top_k": 32,
            },
            stream=False,
        )
        print("Gemini model generated response.")
        print(responses.text)
        
        if responses.text:
            return responses.text.strip()
        else:
            return "None"

    except Exception as e:
        logger.error(f"Gemini analysis failed: {e}")
        return "Error analyzing triggers"
