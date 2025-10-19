# vton/run_vton.py
import os
import torch
from huggingface_hub import snapshot_download
from PIL import Image

from vton.model.cloth_masker import AutoMasker
from model.pipeline import CatVTONPipeline
from utils import init_weight_dtype, resize_and_crop, resize_and_padding


def run_vton(
    person_path: str,
    cloth_path: str,
    result_path: str,
    cloth_type: str = "upper", #옷 종류 "upper", "lower", "overall"
    width: int = 768,
    height: int = 1024,
    num_inference_steps: int = 50,
    guidance_scale: float = 2.5,
    seed: int = -1,
    mixed_precision: str = "fp16",
    allow_tf32: bool = True,
):
    """
    Virtual Try-On 실행 함수
    """

    BASE_MODEL_PATH = "booksforcharlie/stable-diffusion-inpainting"
    RESUME_PATH = "zhengchong/CatVTON"

    # 모델 다운로드
    repo_path = snapshot_download(repo_id=RESUME_PATH)

    # 파이프라인 초기화
    pipeline = CatVTONPipeline(
        base_ckpt=BASE_MODEL_PATH,
        attn_ckpt=repo_path,
        attn_ckpt_version="mix",
        weight_dtype=init_weight_dtype(mixed_precision),
        use_tf32=allow_tf32,
        device="cuda" if torch.cuda.is_available() else "cpu",
        skip_safety_check=True,
    )

    # 마스크 자동 생성기
    automasker = AutoMasker(
        densepose_ckpt=os.path.join(repo_path, "DensePose"),
        schp_ckpt=os.path.join(repo_path, "SCHP"),
        device="cuda" if torch.cuda.is_available() else "cpu",
    )

    # 이미지 로드 및 전처리
    person_image = Image.open(person_path).convert("RGB")
    cloth_image = Image.open(cloth_path).convert("RGB")

    person_image = resize_and_crop(person_image, (width, height))
    cloth_image = resize_and_padding(cloth_image, (width, height))

    # 마스크 생성
    mask = automasker(person_image, cloth_type)["mask"]

    # 시드 고정
    generator = None
    if seed != -1:
        generator = torch.Generator(device=pipeline.device).manual_seed(seed)

    # 추론 실행
    result_image = pipeline(
        image=person_image,
        condition_image=cloth_image,
        mask=mask,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        generator=generator,
    )[0]

    # 저장
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    result_image.save(result_path)

    return result_path
