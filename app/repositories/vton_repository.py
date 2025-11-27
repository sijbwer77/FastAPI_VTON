# app/repositories/vton_repository.py
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import base64
import logging

def _create_image_part(image_bytes: bytes, mime_type: str) -> Part:
    encoded_content = base64.b64encode(image_bytes).decode("utf-8")
    return Part.from_data(data=encoded_content, mime_type=mime_type)

def run_vton_with_vertex_ai(
    person_image_bytes: bytes,
    person_mime_type: str,
    cloth_image_bytes: bytes,
    cloth_mime_type: str,
    cloth_type: str = "upper",
) -> bytes:
    """
    Virtual Try-On with Google Vertex AI (Gemini Flash) using base64 encoded images.
    Returns the generated image as bytes.
    """
    logging.basicConfig(level=logging.INFO)
    try:
        vertexai.init()

        model = GenerativeModel("gemini-2.5-flash-image")

        person_image_part = _create_image_part(person_image_bytes, person_mime_type)
        cloth_image_part = _create_image_part(cloth_image_bytes, cloth_mime_type)

        prompt = [
            f"Please edit the person image to wear the cloth image. The cloth is a {cloth_type} type. # generate only image.",
            person_image_part,
            cloth_image_part,
        ]

        response = model.generate_content(prompt)

        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                # Vertex AI usually returns image/png or image/jpeg
                # Check for inline_data which contains the raw bytes (or base64 depending on client version, usually bytes in Part object if accessed via inline_data.data)
                # Actually, the python client `part.inline_data.data` returns bytes directly if it's populated.
                if part.inline_data and part.inline_data.data:
                    logging.info("Successfully generated image from Vertex AI")
                    return part.inline_data.data
        
        logging.warning("No image parts found in the model response.")
        raise Exception("No image found in the model response.")
    except Exception as e:
        logging.error(f"An error occurred in run_vton_with_vertex_ai: {e}", exc_info=True)
        raise
