# Taiga MCP 서버

Taiga MCP는 [Model Context Protocol(MCP)](https://github.com/model-context-protocol/model-context-protocol) 표준을 사용하여 [Taiga](https://www.taiga.io/) 프로젝트 관리 시스템에 접근할 수 있는 인터페이스를 제공하는 서버입니다. 이를 통해 AI 어시스턴트는 Taiga API와 직접 상호작용하여 프로젝트, 사용자 스토리, 작업 등을 관리할 수 있습니다.

## 주요 기능

- **Taiga API 연동**: Taiga 인스턴스에 연결하여 프로젝트 데이터에 접근
- **사용자 스토리 관리**: 사용자 스토리 조회, 필터링 및 상세 정보 확인
- **작업 관리**: 작업(Task) 목록 조회 및 상세 정보 확인
- **프로젝트 정보**: 프로젝트와 관련된 상태 카테고리 및 상세 정보 조회

## 설치 및 설정

### 필요 조건

- Python 3.10 이상
- Taiga 인스턴스에 대한 접근 권한

### 설치

```bash
# 가상 환경 생성 (선택 사항이지만 권장)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# 의존성 설치
pip install -e .
```

### 환경 설정

`.env` 파일을 생성하고 다음과 같이 구성합니다:

```
TAIGA_API_URL=http://your-taiga-instance.com
TAIGA_USERNAME=your-username
TAIGA_PASSWORD=your-password
TAIGA_DEFAULT_PROJECT=your-default-project-id
```

- `TAIGA_API_URL`: Taiga API의 기본 URL
- `TAIGA_USERNAME`: Taiga에 로그인할 사용자 이름
- `TAIGA_PASSWORD`: Taiga에 로그인할 비밀번호
- `TAIGA_DEFAULT_PROJECT`: (선택 사항) 기본 프로젝트 ID

## 서버 실행

```bash
python src/server.py
```

## MCP 도구

이 서버는 다음과 같은 MCP 도구를 제공합니다:

### `get_project_info`

프로젝트 및 사용자 스토리 상태와 같은 상세 정보를 검색합니다.

### `list_user_stories`

다양한 필터링 옵션을 사용하여 사용자 스토리를 나열합니다.

### `get_user_story`

특정 사용자 스토리에 대한 상세 정보를 가져옵니다.

### `list_tasks`

프로젝트 내의 작업(Task) 목록을 필터링 옵션과 함께 조회합니다.

### `get_task`

특정 작업(Task)의 상세 정보를 조회합니다.

## 개발

### 개발 모드 설치

```bash
pip install -e ".[dev]"
```

### 테스트 실행

```bash
pytest
```

## 라이선스

이 프로젝트는 MIT License로 배포 됩니다.