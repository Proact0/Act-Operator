<div align="center">
  <a href="https://www.proact0.org/">
    <picture>
      <source media="(prefers-color-scheme: light)" srcset=".github/images/light-theme.png">
      <source media="(prefers-color-scheme: dark)" srcset=".github/images/dark-theme.png">
      <img alt="Proact0 Logo" src=".github/images/light-theme.png" width="80%">
    </picture>
  </a>
</div>

<div align="center">
  <h2>Act Operator</h2>
</div>

<div align="center">
  <a href="https://www.apache.org/licenses/LICENSE-2.0" target="_blank"><img src="https://img.shields.io/pypi/l/act-operator" alt="PyPI - License"></a>
  <a href="https://pypistats.org/packages/act-operator" target="_blank"><img src="https://img.shields.io/pepy/dt/act-operator?color=deeppink" alt="PyPI - Downloads"></a>
  <a href="https://pypi.org/project/act-operator/#history" target="_blank"><img src="https://img.shields.io/pypi/v/act-operator" alt="Version"></a>
  <a href="https://www.linkedin.com/company/proact0" target="_blank">
    <img src="https://img.shields.io/badge/LinkedIn-Proact0-blue?logo=linkedin" alt="LinkedIn">
  </a>
  <a href="https://www.proact0.org/" target="_blank">
    <img src="https://img.shields.io/badge/Homepage-Proact0.org-brightgreen?logo=internet-explorer" alt="Homepage">
  </a>
</div>

<br>

Act Operator는 AI 협업 기능이 내장된 구조화된 LangGraph 1.0 프로젝트(Act)를 스캐폴딩하는 프로덕션 레디 CLI입니다.

```bash
uvx --from act-operator act new
```

아키텍처 설계, 개발, 엔지니어링, 테스팅을 위한 전문화된 Agent 스킬이 포함된 쿠키커터 템플릿으로 깔끔하고 모듈화된 그래프 아키텍처를 생성하여, 최적의 유지보수성과 AI 지원 개발로 복잡한 에이전트 워크플로우, 비즈니스 자동화 또는 데이터 파이프라인을 구축할 수 있습니다.

## Act란 무엇인가요?

Act (AX Template)는 프로덕션 수준의 AI 시스템 구축에서 발생하는 일반적인 문제를 해결하도록 설계된 LangGraph 애플리케이션을 위한 표준화된 프로젝트 구조입니다:

- **모듈식 설계**: 각 그래프 컴포넌트(상태, 노드, 에이전트, 도구, 미들웨어 등)는 명확한 책임을 가진 자체 모듈에 존재합니다
- **확장 가능한 아키텍처**: 모노레포 내에서 여러 그래프(캐스트)를 구성하며, 각각 독립적인 패키지로 관리됩니다
- **AI 네이티브 개발**: 내장된 Agent 스킬이 아키텍처 결정, 구현 패턴, 테스팅 전략을 안내합니다
- **초보자 친화적**: 포괄적인 문서와 인라인 가이드로 LangGraph를 처음 접하는 사용자도 쉽게 시작할 수 있습니다

**사용 사례**: 에이전트 AI 시스템, 비즈니스 워크플로우 자동화, 다단계 데이터 파이프라인, 대화형 에이전트, 문서 처리 플로우 또는 **상태 기반 그래프/워크플로우 오케스트레이션이 필요한 모든 애플리케이션**

## 빠른 시작

Python 3.11+ 필요. CLI가 프로젝트 세부 정보를 입력받거나 옵션으로 전달할 수 있습니다.

```bash
# 새로운 Act 프로젝트 생성
uvx --from act-operator act new

# 대화형 프롬프트 따라하기:
# - 경로 & Act 이름: my_workflow
# - Cast 이름: chatbot
```

### 동기화

프로젝트를 생성한 후, 의존성을 설치하고 가상 환경을 동기화합니다:

```bash
uv sync
```

이 명령은 `pyproject.toml`에 정의된 모든 의존성을 설치하고 프로젝트 실행을 준비합니다.


### AI와 함께 빌드 시작하기

Claude Code를 사용하는 경우, 내장된 에이전트 스킬을 활용하여 개발을 가속화할 수 있습니다:

```bash
claude
```

프롬프트에서 스킬 디렉토리를 참조하세요: `.claude/skills`

**사용 가능한 스킬**:
- `architecting-act`: 대화형 질문을 통한 그래프 아키텍처 설계
- `developing-cast`: 모범 사례 패턴으로 노드, 에이전트, 도구 구현
- `engineering-act`: 캐스트 및 의존성 관리, 새로운 캐스트 생성
- `testing-cast`: 모킹 전략을 활용한 효과적인 pytest 테스트 작성

### 스킬 활용하기

스킬은 개별적으로 또는 완전한 워크플로우로 사용할 수 있습니다:

**개별 사용**:
- 프로젝트 아키텍처 설계가 필요하신가요? → `architecting-act` 사용
- 새 캐스트 추가가 필요하신가요? → `engineering-act` 사용
- 특정 노드 구현이 필요하신가요? → `developing-cast` 사용
- 테스트 작성이 필요하신가요? → `testing-cast` 사용

**완전한 워크플로우**:
```plaintext
1. 아키텍처 → "고객 지원 챗봇 설계"
   (architecting-act: 요구사항 가이드, 패턴 제안, CLAUDE.md 생성)

2. 프로젝트 설정(옵션) → "필요한 경우 새 서브 캐스트 생성"
   (engineering-act: 캐스트 구조 스캐폴딩, 의존성 설정)

3. 구현 → "챗봇 구현"
   (developing-cast: state, nodes, agents, tools, graph 생성)

4. 테스팅 → "챗봇에 대한 포괄적인 테스트 작성"
   (testing-cast: LLM/API 모킹을 포함한 pytest 테스트 생성)
```

## 프로젝트 구조

```
my_workflow/
├── .claude/
│   └── skills/                    # AI 협업 가이드
│       ├── architecting-act/      # 아키텍처 설계
│       ├── developing-cast/       # 구현 패턴
│       ├── engineering-act/       # 프로젝트 관리
│       └── testing-cast/          # 테스팅 전략
├── casts/
│   ├── base_node.py              # 베이스 노드 클래스
│   ├── base_graph.py             # 베이스 그래프 유틸리티
│   └── chatbot/                  # 캐스트(그래프 패키지)
│       ├── modules/
│       │   ├── state.py          # 그래프 상태 정의
│       │   ├── nodes.py          # 노드 구현
│       │   ├── agents.py         # 에이전트 설정
│       │   ├── tools.py          # 도구 정의
│       │   ├── models.py         # LLM 모델 설정
│       │   ├── conditions.py     # 라우팅 조건
│       │   ├── middlewares.py    # 커스텀 미들웨어
│       │   └── prompts.py        # 프롬프트 템플릿
│       ├── graph.py              # 그래프 조립
│       └── pyproject.toml        # 캐스트 의존성
├── tests/
│   ├── cast_tests/               # 그래프 레벨 테스트
│   └── node_tests/               # 단위 테스트
├── langgraph.json                # LangGraph 설정
├── pyproject.toml                # 모노레포 의존성
├── TEMPLATE_README.md            # 템플릿 사용 가이드라인
└── README.md
```

## 사용법

### 새로운 캐스트 생성

기존 Act 프로젝트에 다른 그래프 추가하기:

```bash
uv run act cast
# 캐스트 이름과 설정에 대한 대화형 프롬프트
```

### 의존성 추가

```bash
# 모노레포 레벨 (모든 캐스트에서 공유)
uv add langchain-openai

# 캐스트별
uv add --package chatbot langchain-anthropic

# 개발 도구
uv add --dev pytest-mock
```

### 개발 서버 실행

```bash
uv run langgraph dev
```

LangGraph Studio가 `http://localhost:8000`에서 열리며 시각적 그래프 디버깅이 가능합니다.

## 주요 기능

### 1. 구조화된 모듈성

각 모듈은 명확한 가이드라인과 함께 단일 책임을 가집니다:

- **state.py**: 그래프 상태를 위한 TypedDict 스키마 정의
- **nodes.py**: 노드 클래스로 비즈니스 로직 구현
- **agents.py**: 도구와 메모리를 포함한 LLM 에이전트 설정
- **tools.py**: 재사용 가능한 도구 함수 생성
- **conditions.py**: 노드 간 라우팅 로직 정의
- **graph.py**: 컴포넌트를 실행 가능한 그래프로 조립

### 2. AI 지원 개발

내장된 Claude Code 스킬이 워크플로우를 최적화합니다:

- **토큰 효율적**: 불필요한 코드 생성 없이 컨텍스트 인식 가이드 제공
- **대화형**: 아키텍처 스킬은 "20개 질문" 방식으로 요구사항 파악
- **포괄적**: 노드, 에이전트, 도구, 미들웨어, 테스팅을 위한 50개 이상의 구현 패턴
- **공식 문서**: 모든 패턴이 공식 LangChain/LangGraph 문서 참조

### 3. 프로덕션 레디 패턴

실전 검증된 패턴 포함:

- **메모리 관리**: 단기(대화 기록) 및 장기(Store API)
- **안정성**: 재시도 로직, 폴백, 오류 처리
- **안전성**: 가드레일, 속도 제한, 인간 승인 단계
- **관찰성**: LangSmith 통합, 구조화된 로깅
- **테스팅**: 모킹 전략, 픽스처, 커버리지 가이드라인

### 4. 초보자 친화적

LangChain/LangGraph 입문자에게 완벽합니다:

- 단계별 구현 가이드
- 패턴 결정 매트릭스
- 유용한 프롬프트를 제공하는 대화형 CLI
- 포괄적인 인라인 문서
- 일반적인 사용 사례를 위한 예제 패턴

## CLI 명령어

```bash
# 새로운 Act 프로젝트 생성
act new [OPTIONS]
  --act-name TEXT       프로젝트 이름
  --cast-name TEXT      초기 캐스트 이름
  --path PATH           대상 디렉토리

# 기존 프로젝트에 캐스트 추가
act cast [OPTIONS]
  --cast-name TEXT      캐스트 이름
  --path PATH           Act 프로젝트 디렉토리
```

## 사용 사례 예시

### 에이전트 AI 시스템

멀티 에이전트 패턴을 사용하여 전문화된 역할(연구원, 작가, 검토자)을 가진 다중 에이전트 시스템 구축.

### 비즈니스 워크플로우 자동화

조건부 분기, 인간 승인 단계, 외부 API 통합을 포함한 복잡한 비즈니스 프로세스 오케스트레이션.

### 데이터 처리 파이프라인

오류 처리 및 재시도 로직을 포함한 순차 또는 병렬 데이터 변환 그래프 생성.

### 대화형 AI

메모리 관리, 도구 호출, 가드레일을 갖춘 컨텍스트 인식 챗봇 개발.

## 기여하기

커뮤니티의 기여를 환영합니다! 기여 가이드를 읽어주세요:

- [CONTRIBUTING.md](CONTRIBUTING.md) (영어)

### 기여자

모든 기여자분들께 감사드립니다! 여러분의 기여가 Act Operator를 더 나아지게 만듭니다.

<a href="https://github.com/Proact0/Act-Operator/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Proact0/Act-Operator" />
</a>

## 라이선스

Apache License 2.0 - 자세한 내용은 [LICENSE](https://www.apache.org/licenses/LICENSE-2.0) 참조.

---

<div align="center">
  <p><a href="https://www.proact0.org/">Proact0</a>가 ❤️로 만들었습니다</p>
  <p>Act (AX Template) 표준화 및 AI 생산성 향상을 위한 비영리 오픈소스 허브</p>
</div>
