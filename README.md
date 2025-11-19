# FastAPI VTON

## Overview

This project is a web application that provides a virtual try-on (VTON) service. Users can upload photos of themselves and clothes, and the system will generate an image of the user wearing the selected clothes.

## Features

-   **User Authentication:** Secure user registration and login system.
-   **Photo Upload:** Users can upload their full-body photos and images of clothes.
-   **Virtual Try-On:** Generates a realistic image of the user wearing the selected garment.
-   **Image Gallery:** Browse uploaded clothes and view past try-on results.
-   **RESTful API:** Well-defined API for managing users, images, and try-on processes.

## 1. 환경 설정

프로젝트를 실행하기 위한 환경 설정 단계는 다음과 같습니다.

### 1.1. 가상 환경 생성 및 활성화

Python 가상 환경(venv)을 사용하여 프로젝트 종속성을 격리하는 것을 권장합니다.

```bash
python -m venv venv
```

가상 환경을 활성화합니다:

-   **Windows:**
    ```bash
    .\venv\Scripts\activate
    ```
-   **macOS/Linux:**
    ```bash
    source venv/bin/activate
    ```

### 1.2. 종속성 설치

가상 환경이 활성화된 상태에서 `requirements.txt` 파일에 명시된 모든 종속성을 설치합니다.

```bash
pip install -r requirements.txt
```

## 2. 환경 변수 설정

프로젝트는 `.env` 파일의 환경 변수를 사용하여 주요 설정을 관리합니다.

1.  프로젝트 루트 디렉토리에서 `.env.example` 파일을 복사하여 `.env` 파일을 생성합니다.
    ```bash
    cp .env.example .env
    ```
2.  `.env` 파일을 열어 자신의 환경에 맞게 변수들을 수정합니다.

## 3. 프로젝트 실행

모든 종속성이 설치되면, 다음 명령어를 사용하여 FastAPI 애플리케이션을 실행할 수 있습니다.

```bash
uvicorn app.main:app
```

애플리케이션이 성공적으로 실행되면, `http://localhost:8000`에서 접근할 수 있습니다.

## 4. API Endpoints

주요 API 엔드포인트는 다음과 같습니다. 전체 API 문서는 서버 실행 후 `http://localhost:8000/docs`에서 확인하세요.

| Method | Path                  | Description                               |
| :----- | :-------------------- | :---------------------------------------- |
| POST   | /register             | 회원가입                                  |
| POST   | /token                | 로그인 (액세스 토큰 발급)                 |
| GET    | /users/me             | 현재 로그인된 사용자 정보 조회            |
| POST   | /upload/person        | 개인 사진 업로드                          |
| POST   | /upload/cloth         | 옷 사진 업로드                            |
| GET    | /images/{category}    | 카테고리별 이미지 목록 조회               |
| POST   | /tryon                | 가상 피팅 실행                            |

## 5. 프로젝트 구조

주요 디렉토리 구조와 역할은 다음과 같습니다.

```
├── app/                # FastAPI 애플리케이션의 핵심 로직
│   ├── routes/         # API 엔드포인트 정의
│   ├── services/       # 비즈니스 로직 처리
│   ├── repositories/   # 데이터베이스 상호작용
│   └── main.py         # FastAPI 앱 초기화 및 설정
├── vton/               # 가상 피팅(VTON) 딥러닝 모델 및 실행 스크립트
├── public/             # 프론트엔드 정적 파일 (HTML, CSS, JS)
├── resources/          # 사용자가 업로드한 원본 이미지 저장
└── .env                # 환경 변수 설정 파일
```