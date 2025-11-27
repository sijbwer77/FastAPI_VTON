# app/services/vton_service.py
from app.repositories import vton_repository

def run_vton(
    person_image_bytes: bytes,
    person_mime_type: str,
    cloth_image_bytes: bytes,
    cloth_mime_type: str,
    cloth_type: str
) -> bytes:
    return vton_repository.run_vton_with_vertex_ai(
        person_image_bytes,
        person_mime_type,
        cloth_image_bytes,
        cloth_mime_type,
        cloth_type
    )