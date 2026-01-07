---
description: 새 cast 패키지 생성, 의존성 설치/관리 (monorepo 또는 cast 레벨), 의존성 충돌 해결, langgraph dev 서버 실행 시 사용. CLAUDE.md를 먼저 확인한 후 모든 uv 기반 프로젝트 설정 및 패키지 관리 (dev/test/lint 그룹) 처리.
---

# Act 엔지니어링

Backand Act 프로젝트 설정, 의존성, cast 스캐폴딩 관리.

## 사용하지 말 것

- casts/nodes 구현 → `developing`
- 아키텍처 설계 → `architecting`
- 테스트 작성 → `testing`

## 워크플로우

**모든 작업 전:**
1. CLAUDE.md 파일 확인 (존재하는 경우)
   - **루트 `/CLAUDE.md`**: Act 개요와 Casts 테이블 검토
   - **Cast `/casts/{cast_slug}/CLAUDE.md`**: cast별 의존성과 기술 스택 검토
2. 아래 작업 진행

## 작업

| 작업 | 리소스 |
|------|--------|
| 새 cast(패키지) 생성 | `resources/create-cast.md` |
| act(monorepo) 의존성 추가 | `resources/add-dep-act.md` |
| cast(패키지) 의존성 추가 | `resources/add-dep-cast.md` |
| 환경 동기화 | `resources/sync.md` |

## 빠른 참조

```bash
# 1. CLAUDE.md 파일 확인 (있는 경우)
#    루트 /CLAUDE.md: 테이블에서 기존 Casts 검토
#    Cast /casts/{cast_slug}/CLAUDE.md: Technology Stack 섹션 확인

# 2. Cast 생성
uv run act cast -c "My Cast"

# 3. 의존성 추가 (cast의 CLAUDE.md Technology Stack 참고)
uv add langchain-openai              # Monorepo (프로덕션)
uv add --dev pytest-mock             # Monorepo (개발)
uv add --package my_cast langchain-openai  # Cast 패키지

# 4. 동기화
uv sync --all-packages            # 개발
uv sync --all-packages --no-dev   # 프로덕션

# 5. LangGraph 서버
uv run langgraph dev
uv run langgraph dev --tunnel        # 비-Chrome 브라우저
```

## 의존성 그룹

| 그룹 | 플래그 | 내용 |
|------|--------|------|
| dev | `--dev` | act-operator + test + lint |
| test | `--group test` | pytest, langgraph-cli[inmem] |
| lint | `--group lint` | pre-commit, ruff |
