# app/services/vton_service.py
from app.repositories import vton_repository

def run_vton(person_path: str, cloth_path: str, cloth_type: str):
    return vton_repository.run_vton_with_vertex_ai(person_path, cloth_path, cloth_type)
