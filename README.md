# Undervalued Stock Notifier

DDD(Domain-Driven Design) 아키텍처를 적용한 저평가 주식 스캔 및 알림 프로그램입니다. 한국(Naver Finance)과 미국(Yahoo Finance) 시장의 데이터를 분석하여 Discord로 알림을 보냅니다.

## 주요 특징
- **No Login / No API Key**: KRX 공식 API나 로그인 과정 없이 네이버 금융 크롤링을 통해 한국 주식 정보를 무료로 가져옵니다.
- **DDD 구조**: 유지보수와 확장이 쉬운 계층형 아키텍처를 따릅니다.
- **현대적인 의존성 관리**: `requirements.txt` 대신 `pyproject.toml`을 사용하여 의존성을 관리합니다.
- **보안**: `direnv`를 활용하여 Discord Webhook URL 등 민감한 설정을 보호합니다.

## 프로젝트 시작하기

### 1. 환경 설정 (`direnv`)
프로젝트 루트에서 환경 변수를 설정합니다.
```bash
cp .envrc.template .envrc
# .envrc 파일을 편집하여 DISCORD_WEBHOOK_URL을 입력하세요.
direnv allow
```

### 2. 패키지 설치 (`pyproject.toml`)
`pip`를 통해 프로젝트와 의존성을 설치합니다.
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

### 3. 프로그램 실행
```bash
export PYTHONPATH=$PYTHONPATH:.
python3 src/main.py
```

## 테스트 실행 (AAA 패턴)
도메인 레이어의 비즈니스 로직을 테스트합니다.
```bash
# 테스트용 의존성 추가 설치
pip install ".[test]"

# 테스트 실행
export PYTHONPATH=$PYTHONPATH:.
pytest tests/domain/test_strategy.py
```

## 해결된 이슈 (Troubleshooting)
- **KRX 로그인 문제**: `Pykrx` 라이브러리의 보안 정책 변경 이슈를 해결하기 위해, 로그인 없이 사용 가능한 **Naver Finance 크롤러(`NaverAdapter`)**로 교체했습니다.
- **의존성 관리**: `requirements.txt`를 제거하고 `pyproject.toml` 기반으로 통합했습니다.
- **Scraping 오류**: `pandas.read_html` 시 발생하는 의존성(`lxml`, `html5lib`) 문제를 `pyproject.toml`에 반영하여 해결했습니다.
