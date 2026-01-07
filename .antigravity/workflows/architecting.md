---
description: Act/Cast 아키텍처 설계 - 새 Act 프로젝트 시작, 기존 Act에 cast 추가, 복잡한 cast의 sub-cast 추출 시 사용. 대화형 질문을 통해 요구사항에서 검증된 아키텍처까지 mermaid 다이어그램과 함께 안내. 설계 우선, 코드 생성 없음.
---

# Act 아키텍처 설계

Act(프로젝트)와 Cast(그래프) 아키텍처를 대화형 질문을 통해 설계하고 관리합니다. 프로젝트 루트에 Act 개요와 모든 Cast 명세가 포함된 `CLAUDE.md`를 출력합니다.

## 사용 시점

- 초기 Act 아키텍처 계획 (`act new` 이후)
- 기존 Act에 새 Cast 추가
- Cast 복잡도 분석을 통한 Sub-Cast 추출
- 아키텍처 설계에 대한 불확실성

## 사용하지 말 것

- 코드 구현 → `developing` 워크플로우 사용
- cast 파일 생성 → `engineering` 워크플로우 사용
- 테스트 작성 → `testing` 워크플로우 사용

---

## 핵심 원칙

**대화형**: 한 번에 하나의 질문만. 응답을 기다린 후 진행.

**코드 없음**: 구조만 설명. TypedDict, 함수, 구현 코드 없음.

**다이어그램에 엣지 표시**: Mermaid 다이어그램에 모든 노드와 엣지 포함. 별도 테이블 없음.

---

## 모드 감지

**먼저 모드 결정:**

- **CLAUDE.md 없음?** → **모드 1: 초기 설계**
- **CLAUDE.md 있음 + cast 추가?** → **모드 2: Cast 추가**
- **CLAUDE.md 있음 + cast 복잡?** → **모드 3: Sub-Cast 추출**

---

## 모드 1: 초기 설계

**시점:** 첫 설계 시 (CLAUDE.md 없음)

**단계:**
1. **Backand Act 질문** → 리소스 `modes/initial-design-questions.md` 참고
   - Act 목적, Cast 식별, Cast 목표, 입출력, 제약조건
2. **Chat Cast 설계** → 아래 "Cast 설계 워크플로우" 따르기
3. **CLAUDE.md 파일 생성** → 리소스 `act-template.md`, `cast-template.md` 사용
   - `/CLAUDE.md` 생성 (Act 정보 + Casts 테이블)
   - `/casts/chat/CLAUDE.md` 생성 (Cast 세부사항)
4. **검증** → 검증 스크립트 실행

---

## 모드 2: Cast 추가

**시점:** CLAUDE.md 있음, 새 cast 추가

**단계:**
1. **CLAUDE.md 읽기** → 기존 Backand Act와 Casts 이해
2. **질문** → 리소스 `modes/add-cast-questions.md` 참고
3. **Cast 설계** → 아래 "Cast 설계 워크플로우" 따르기
4. **Cast 패키지 생성** → `uv run act cast -c "{새 Cast 이름}"` 실행
5. **CLAUDE.md 파일 업데이트**
6. **검증** → 검증 스크립트 실행

---

## 모드 3: Sub-Cast 추출

**시점:** Cast가 10개 이상 노드 또는 복잡도 언급됨

**단계:**
1. **분석** → 리소스 `cast-analysis-guide.md` 사용
2. **질문** → 리소스 `modes/extract-subcast-questions.md` 참고
3. **Sub-Cast 설계** → 아래 "Cast 설계 워크플로우" 따르기
4. **Sub-Cast 패키지 생성** → `uv run act cast -c "{Sub-Cast 이름}"` 실행
5. **CLAUDE.md 파일 업데이트**
6. **검증** → 검증 스크립트 실행

---

## Cast 설계 워크플로우

**모든 모드에서 cast 설계 시 사용:**

### 1. 패턴 선택

리소스 `pattern-decision-matrix.md` 사용하여 **패턴 제안**:

| 요구사항 | 패턴 |
|---------|------|
| 선형 변환 | Sequential |
| 다중 핸들러 | Branching |
| 개선 루프 | Cyclic |
| 전문 역할 | Multi-agent |

질문: "이 패턴이 맞나요?" 확인 대기.

### 2. 상태 스키마

리소스 `design/state-schema.md` 사용하여 **스키마 설계**.

**테이블만** 제시 (InputState, OutputState, OverallState).

질문: "수정할 필드가 있나요?" 응답 대기.

### 3. 노드 명세

리소스 `design/node-specification.md` 사용, **패턴별 질문**:
- Sequential/Branching: "주요 처리 단계?" (3-7 노드)
- Cyclic: "개선 대상? 종료 조건?"
- Multi-agent: "전문 역할은?"

**노드 설계** (단일 책임, CamelCase 명명).

### 4. 아키텍처 다이어그램

리소스 `design/edge-routing.md` 사용하여 **Mermaid 다이어그램 생성**.

확인: 모든 노드 연결, 모든 경로 END 도달, 조건 레이블 지정.

### 5. 기술 스택

> `langgraph`, `langchain` 포함. **추가** 의존성만 식별.

**한 번에 하나씩 질문:**
1. LLM 제공자? → 대기
2. 벡터 스토어? → 대기
3. 검색 도구? → 대기
4. 문서 유형? → 대기

패키지 + 환경 변수 **결정**.

### 6. 검증

```bash
python .claude/skills/architecting-act/scripts/validate_architecture.py
```

리소스 `validation-checklist.md` 참고.

문제 발견 시 수정 후 요약 제시.
