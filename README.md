# FastAPI VTON 

## 2. 환경 설정

프로젝트를 실행하기 위한 환경 설정 단계는 다음과 같습니다.

### 2.1. 가상 환경 생성 및 활성화

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

### 2.2. 종속성 설치

가상 환경이 활성화된 상태에서 `requirements.txt` 파일에 명시된 모든 종속성을 설치합니다.

```bash
pip install -r requirements.txt
```

## 3. 프로젝트 실행

모든 종속성이 설치되면, 다음 명령어를 사용하여 FastAPI 애플리케이션을 실행할 수 있습니다.

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

애플리케이션이 성공적으로 실행되면, `http://0.0.0.0:8000` 또는 `http://localhost:8000`에서 접근할 수 있습니다.
FastAPI의 자동 생성된 API 문서는 `http://localhost:8000/docs`에서 확인할 수 있습니다.