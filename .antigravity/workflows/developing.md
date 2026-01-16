---
description: LangGraph 컴포넌트(state, nodes, edges, graph) 구현 - CLAUDE.md 명세 유무와 관계없이 사용. 워크플로우 순서(구현 순서), agents/models/tools/memory/middlewares/prompts 패턴(대화 메모리, 재시도/폴백, 가드레일, 벡터 스토어, 도구 관리 등) 필요 시 사용. 체계적 워크플로우 제공 (state → deps → nodes → conditions → graph)
---

# Cast 개발

Backand Act 패턴을 따르는 LangGraph cast 구현.

## 사용 시점

- 노드, 에이전트, 도구, 그래프 구축
- LangGraph 구현 패턴 필요
- 구현할 아키텍처 명세 있음

## 사용하지 말 것

- 아키텍처 설계 → `architecting`
- 프로젝트 설정 → `engineering`
- 테스트 → `testing`

---

## 구현 워크플로우

### Step 1: CLAUDE.md 이해

**CLAUDE.md 있는 경우 (분산 구조):**
- **루트 `/CLAUDE.md`** 내용:
  - **Act 개요**: Backand Act 목적과 도메인
  - **Casts 테이블**: 프로젝트 내 모든 cast와 링크
- **Cast `/casts/{cast_slug}/CLAUDE.md`** 내용:
  - **Cast 개요**: 목적, 패턴, 레이턴시
  - **아키텍처 다이어그램**: 노드와 엣지가 있는 Mermaid 다이어그램
  - **상태 스키마**: InputState, OutputState, OverallState
  - **노드 명세**: 상세 노드 설명
  - **기술 스택**: 추가 의존성과 환경 변수

**CLAUDE.md 없는 경우:**
- 아키텍처 분석 건너뛰기
- Step 2로 진행

### Step 2: 구현

**순서대로 구현:** state → 의존성 모듈 → nodes → conditions → graph

```
1. State (state.py)           # 기초
   ↓
2. 의존성 모듈                 # agents, models, tools, prompts, middlewares, utils
   ↓
3. Nodes (nodes.py)           # 비즈니스 로직
   ↓
4. Conditions (conditions.py) # 라우팅 함수 (필요시)
   ↓
5. Graph (graph.py)           # 조립
```

### Option Step 3: 환경 변수 생성 (필요시)

`.env.example` 업데이트 (프로젝트 루트)

```bash
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

### Option Step 4: 의존성 패키지 설치 (필요시)

`engineering` 워크플로우 사용

---

## 컴포넌트 레퍼런스

### 코어 컴포넌트

| 사용 시점 | 리소스 |
|-----------|--------|
| TypedDict로 그래프 상태 정의 | `usage/core/state.md` |
| sync/async 노드 클래스 구현 | `usage/core/node.md` |
| 엣지 또는 조건부 라우팅 설정 | `usage/core/edge.md` |
| StateGraph 조립 및 컴파일 | `usage/core/graph.md` |
| 그래프를 서브그래프로 재사용 | `usage/core/subgraph.md` |

### 프롬프트 & 메시지

| 사용 시점 | 리소스 |
|-----------|--------|
| System/Human/AI/Tool 메시지 생성 | `usage/prompts/message-types.md` |
| 이미지/오디오/PDF 입력 처리 | `usage/prompts/multimodal.md` |

### 모델 & 에이전트

| 사용 시점 | 리소스 |
|-----------|--------|
| OpenAI/Anthropic/Google 선택 | `usage/models/select-chat-models.md` |
| 모델 설정 (temperature, tokens) | `usage/models/standalone-model.md` |
| 모델 구조화된 출력 (Pydantic) | `usage/models/structured-output.md` |
| 도구가 있는 에이전트 생성 | `usage/agents/configuration.md` |
| 에이전트 구조화된 출력 (Pydantic) | `usage/agents/structured-output.md` |

### 도구

| 사용 시점 | 리소스 |
|-----------|--------|
| @tool로 간단한 도구 생성 | `usage/tools/basic-tool.md` |
| 복잡한 Pydantic 입력 도구 | `usage/tools/tool-with-complex-inputs.md` |
| 상태/스토어 읽기/쓰기 도구 | `usage/tools/access-context.md` |

### 메모리

| 사용 시점 | 리소스 |
|-----------|--------|
| 에이전트에 대화 메모리 추가 | `usage/memory/short-term/add-to-agent.md` |
| 에이전트 메모리 스토리지 커스터마이즈 | `usage/memory/short-term/customize-agent-memory.md` |
| 히스토리 트리밍/삭제/요약 | `usage/memory/short-term/manage-conversations.md` |
| 미들웨어/도구에서 메모리 접근 | `usage/memory/short-term/access-and-modify-memory.md` |
| 세션 간 데이터 영속화 (Store) | `usage/memory/long-term/memory-storage.md` |
| 도구 내에서 Store 접근 | `usage/memory/long-term/in-tools.md` |

### 미들웨어 - 신뢰성

| 사용 시점 | 리소스 |
|-----------|--------|
| LLM 호출 간헐적 실패 | `usage/middlewares/provider-agnostic/model-retry.md` |
| 도구 실행 간헐적 실패 | `usage/middlewares/provider-agnostic/tool-retry.md` |
| 기본 모델 실패 시 백업 모델 필요 | `usage/middlewares/provider-agnostic/model-fallback.md` |

### 미들웨어 - 안전 & 제어

| 사용 시점 | 리소스 |
|-----------|--------|
| 부적절한 콘텐츠 검증/차단 | `usage/middlewares/provider-agnostic/guardrails.md` |
| 무한 LLM 호출 루프 방지 | `usage/middlewares/provider-agnostic/model-call-limit.md` |
| 비용 제어를 위한 도구 호출 제한 | `usage/middlewares/provider-agnostic/tool-call-limit.md` |
| 체크포인트에서 사람 승인 요구 | `usage/middlewares/provider-agnostic/human-in-the-loop.md` |

### 미들웨어 - 도구 관리

| 사용 시점 | 리소스 |
|-----------|--------|
| 관련 도구 동적 선택 | `usage/middlewares/provider-agnostic/llm-tool-selector.md` |
| 테스트용 LLM으로 도구 에뮬레이션 | `usage/middlewares/provider-agnostic/llm-tool-emulator.md` |
| 에이전트에 영속 쉘 세션 필요 | `usage/middlewares/provider-agnostic/shell-tool.md` |
| 에이전트에 파일 검색 (glob/grep) 필요 | `usage/middlewares/provider-agnostic/file-search.md` |
| 에이전트에 작업 계획/추적 필요 | `usage/middlewares/provider-agnostic/to-do-list.md` |

### 미들웨어 - 컨텍스트

| 사용 시점 | 리소스 |
|-----------|--------|
| 런타임에 메시지 수정/제거 | `usage/middlewares/provider-agnostic/context-editing.md` |
| 토큰 제한 근처 자동 요약 | `usage/middlewares/provider-agnostic/summarization.md` |

### 미들웨어 - 제공자별

| 사용 시점 | 리소스 |
|-----------|--------|
| OpenAI moderation API 사용 | `usage/middlewares/provider-specific/openai.md` |
| Claude 캐싱/bash/text-editor 사용 | `usage/middlewares/provider-specific/anthropic.md` |
| 커스텀 before/after/wrap 훅 구축 | `usage/middlewares/custom.md` |

### 통합

| 사용 시점 | 리소스 |
|-----------|--------|
| 텍스트를 임베딩 벡터로 변환 | `usage/integrations/embedding.md` |
| FAISS/Pinecone/Chroma 스토어 사용 | `usage/integrations/vector-stores.md` |
| 긴 문서를 청크로 분할 | `usage/integrations/text-spliter.md` |

---

## 검증

- [ ] CLAUDE.md 확인 (존재하면 루트 + cast별, 없으면 건너뛰기)
- [ ] 파일 순서: state → 의존성 모듈 → nodes → conditions → graph
- [ ] graph.py에서 노드 이름 소문자
- [ ] `langgraph.graph`에서 START/END import
- [ ] 노드 인스턴스로 추가
- [ ] 그래프 컴파일 성공

---

## 다음 단계

1. **테스트:** `testing` 워크플로우
2. **디버그:** `uv run langgraph dev`
