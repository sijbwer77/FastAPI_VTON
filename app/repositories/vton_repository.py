# app/repositories/vton_repository.py
import os
import uuid
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import base64
import io
from PIL import Image as PILImage
import logging # Added logging import

def _load_image_as_base64_part(image_path: str) -> Part:
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    encoded_content = base64.b64encode(image_bytes).decode("utf-8")
    # Determine MIME type based on file extension
    mime_type = "image/png" # Default
    if image_path.lower().endswith(".jpg") or image_path.lower().endswith(".jpeg"):
        mime_type = "image/jpeg"
    elif image_path.lower().endswith(".webp"):
        mime_type = "image/webp"
    return Part.from_data(data=encoded_content, mime_type=mime_type)

def run_vton_with_vertex_ai(
    person_path: str,
    cloth_path: str,
    cloth_type: str = "upper",
):
    """
    Virtual Try-On with Google Vertex AI (Gemini Flash) using base64 encoded images.
    """
    logging.basicConfig(level=logging.INFO) # Added logging config
    try: # Added try block
        vertexai.init()

        model = GenerativeModel("gemini-2.5-flash-image")

        person_image_part = _load_image_as_base64_part(person_path)
        cloth_image_part = _load_image_as_base64_part(cloth_path)

        result_path = f"resources/results/{uuid.uuid4()}.png"

        prompt = [
            f"Please edit the person image to wear the cloth image. The cloth is a {cloth_type} type. # generate only image.",
            person_image_part,
            cloth_image_part,
        ]

        response = model.generate_content(prompt)
        # logging.info(f"Vertex AI Response: {response}") # Added logging

        # Assuming the response contains an image in the first part of the first candidate
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.mime_type and part.mime_type.startswith(""):
                    image_data_bytes = base64.b64decode(part.inline_data.data) # Renamed variable for clarity
                    image_data_bytes = part.inline_data.data
                    image_stream = io.BytesIO(image_data_bytes)
                    pil_image = PILImage.open(image_stream)
                    
                    # Ensure the results directory exists
                    os.makedirs(os.path.dirname(result_path), exist_ok=True) # Added os.makedirs

                    pil_image.save(result_path) # Changed to PIL save
                    logging.info(f"Successfully saved image to {result_path}") # Added logging
                    return result_path
        
        logging.warning("No image parts found in the model response.") # Added logging
        raise Exception("No image found in the model response.")
    except Exception as e: # Added except block
        logging.error(f"An error occurred in run_vton_with_vertex_ai: {e}", exc_info=True) # Added logging
        raise