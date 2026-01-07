# 컨트리뷰팅 가이드

- Read this in English: [CONTRIBUTING.md](CONTRIBUTING.md)

Act Operator 오픈소스 프로젝트에 관심 가져주셔서 감사합니다! 우리는 **모든 형태의 기여**를 환영합니다—버그 리포트, 문서 개선, 테스트 추가, 기능 제안/구현, 개발자 경험 향상 등. 작고 명확한 변경과 친절한 설명, 충분한 테스트가 좋은 협업을 만듭니다.

## 목차

- [빠른 시작](#빠른-시작)
- [기여하기 전에](#기여하기-전에)
- [기여 범위](#기여-범위)
- [기여 유형별 가이드](#기여-유형별-가이드)
  - [버그 수정](#버그-수정)
  - [새 기능 제안 및 구현](#새-기능-제안-및-구현)
  - [문서 개선](#문서-개선)
  - [Claude Agent Skill 기여](#claude-agent-skill-기여)
- [코드 품질 기준](#코드-품질-기준)
- [테스트 작성](#테스트-작성)
- [LLM을 활용한 기여](#llm을-활용한-기여)
- [하위 호환성 정책](#하위-호환성-정책)
- [PR 및 코드 리뷰](#pr-및-코드-리뷰)
- [버전 및 릴리즈](#버전-및-릴리즈)
- [커뮤니티](#커뮤니티)

---

## 빠른 시작

### 요구사항

- **Python 3.11+**
- **uv**: 의존성 관리 도구

설치 가이드: [uv Installation](https://docs.astral.sh/uv/getting-started/installation/)

```bash
pip install uv
```

### 개발 환경 구성

```bash
# 리포지토리 클론
git clone https://github.com/Proact0/Act-Operator.git
cd Act-Operator/act_operator

# 의존성 설치
uv sync

# 로컬에서 CLI 실행
uv run act new --path ./test-act --act-name "Test" --cast-name "Main"

# 테스트 실행 시
uv run pytest
```

---

## 기여하기 전에

### 💬 논의 우선

**대규모 변경사항은 구현 전에 반드시 논의하세요:**

- **디스코드**: https://discord.gg/4GTNbEy5EB
- **GitHub Issues**: [새 이슈 생성](https://github.com/Proact0/act-operator/issues/new/choose)

**논의가 필요한 경우:**
- 새로운 CLI 명령어 추가
- 스캐폴드 템플릿 구조 변경
- 하위 호환성에 영향을 주는 변경
- 새로운 의존성 추가
- 아키텍처 변경

**논의 없이 진행 가능:**
- 버그 수정 (기존 동작 복구)
- 문서 오탈자 수정
- 테스트 추가
- 코드 포맷팅 개선

### 📋 이슈 템플릿 사용

기여 전 관련 이슈를 확인하거나 새로 생성하세요:

- **버그 리포트**: [Bug Report 템플릿](https://github.com/Proact0/act-operator/issues/new?template=bug-report-kr.yml)
- **기능 제안**: [Backlog 템플릿](https://github.com/Proact0/act-operator/issues/new?template=backlog-kr.yml)

---

## 기여 범위

Act Operator 프로젝트는 여러 컴포넌트로 구성되어 있습니다.

### 1️⃣ Act Operator CLI (현재 레포지토리)

**위치**: `act_operator/`

**포함 내용**:
- CLI 명령어 (`act new`, `act cast`)
- cookiecutter 스캐폴드 생성 로직
- 빌드/배포 프로세스

### 2️⃣ 스캐폴드 템플릿

**위치**: `act_operator/scaffold/`

**포함 내용**:
- 프로젝트 구조 템플릿
- 베이스 클래스 (`base_node.py`, `base_graph.py`)

### 3️⃣ Claude Agent Skills

**위치**: `act_operator/scaffold/{{ cookiecutter.act_slug }}/.claude/skills/`

**포함 스킬**:
- `architecting-act`: 아키텍처 설계
- `developing-cast`: 구현 패턴
- `engineering-act`: 프로젝트 관리
- `testing-cast`: 테스팅 전략

### 4️⃣ 문서 (별도 레포)

**위치**: [Proact0 Docs](https://github.com/Proact0/docs)

**포함 내용**:
- 사용자 가이드
- 튜토리얼
- 패턴 라이브러리
- 기타 유용한 팁

---

## 기여 유형별 가이드

### 버그 수정

**워크플로우:**

1. 버그 재현 및 최소 재현 케이스 작성
2. 이슈 생성 (재현 절차, 환경 정보, 예상/실제 동작)
3. 브랜치 생성: `git checkout -b fix/issue-123-descriptive-name`
4. 수정 구현 (최소한의 변경, 근본 원인 해결)
5. 로컬 테스트: `uv run ruff check .`, 재현 케이스로 확인
6. PR 제출 (`Fixes #123` 포함, 변경 사항 및 테스트 방법 명시)

### 새 기능 제안 및 구현

**⚠️ 구현 전 반드시 논의 필요**

1. 디스코드 또는 이슈에서 제안 (문제, 해결 방법, 대안, 사용 사례)
2. 메인테이너 승인 및 구현 방향 합의
3. 브랜치 생성: `git checkout -b feat/descriptive-feature-name`
4. 구현 (타입 힌트, 독스트링, 문서 업데이트)
5. 테스트 작성 (새 기능 검증, 엣지 케이스)
6. PR 제출

### 문서 개선

**문서 유형:**

| 유형 | 대상 | 내용 | 위치 | 비고 |
|------|------|------|------|------|
| 📘 사용자 가이드 | Act Operator 사용자 | 설치, 사용법, 예제 | `README.md`, `README_KR.md` | |
| 📙 기여 가이드 | 기여자 | 개발 환경, 워크플로우 | `CONTRIBUTING.md`, `CONTRIBUTING_KR.md` | Proact0 Docs로 이전 예정 |
| 📗 스킬 문서 | Claude Agent | 아키텍처, 구현 가이드 등 Agent Skills | `.claude/skills/*/SKILL.md` | |
| 📕 상세 문서 | 심화 사용법, 학습 사용자 | 튜토리얼, 패턴 | [Proact0 Docs](https://docs.proact0.org/) | |

**작성 가이드:**
- ✅ 명확하고 간결하게
- ✅ 실행 가능한 예제 포함
- ✅ 중복 방지: 한 곳에만 기술, 나머지는 링크
- ✅ 접근성: 스크린 리더 고려, 대체 텍스트 제공

### Claude Agent Skill 기여

**Skill 구조:**

```
.claude/skills/<skill-name>/
├── SKILL.md              # 메인 문서 (필수)
├── resources/            # 참조 문서 (선택)
│   └── *.md
└── scripts/              # 유틸리티 스크립트 (선택)
    └── *.py
```

**기여 유형:**

1. **기존 Skill 개선**: 오탈자 수정, 설명 명확화, 예제 추가
2. **새 Skill 작성**: 완전히 새로운 Skill 설계 및 구현

**새 Skill 작성 요구사항:**

- **Frontmatter (YAML)**:
  ```yaml
  ---
  name: skill-name-with-hyphens
  description: Use when [언제 사용] - [무엇을 하는지]
  ---
  ```
- **명확한 사용 시점**: "Use this skill when:" 섹션
- **구조화된 내용**: Workflow/Task/Reference 패턴
- **실용적 예제**: 코드 샘플, 체크리스트
- **일관된 스타일**: 기존 Skill 참고

**권장: TDD 방식 검증**

`.claude/skills/writing-skills` 가이드 참조:
1. 압력 시나리오 작성
2. Skill 없이 실행 (베이스라인)
3. Skill 작성
4. Skill과 함께 재실행
5. 취약점 발견 및 개선

**Skill 기여 체크리스트:**
- [ ] Frontmatter (`name`, `description`) 포함
- [ ] "Use this skill when:" 섹션 명확
- [ ] 구조화된 내용
- [ ] 예제 및 코드 샘플
- [ ] 기존 Skill과 일관된 스타일
- [ ] (권장) 서브에이전트 테스트 완료

---

## 코드 품질 기준

### 타입 힌트 (Type Hints)

**필수**: 모든 함수에 대한 완전한 타입 어노테이션을 작성해야 합니다.

```python
def build_name_variants(name: str) -> NameVariants:
    """Build name variants from display name.

    Args:
        name: Display name to convert.

    Returns:
        NameVariants object with snake_case and slug forms.
    """
    # implementation
```

### 독스트링 (Docstrings)

**필수** : 모든 공개 함수에 [Google 스타일의 문서 문자열](https://google.github.io/styleguide/pyguide.html)을 작성해야 합니다.
**기본 원칙** : Docstring은 "무엇"을 설명하고, [Docs](https://docs.proact0.org/)는 "어떻게"와 "왜"를 설명합니다.

**독스트링에는 다음 내용이 포함되어야 합니다:**

1. 클래스/함수의 기능을 한 줄로 요약한 설명
2. 튜토리얼, 가이드 및 사용 사례 Docs 링크 (해당 시)
3. 매개변수 유형 및 설명
4. 반환 값 설명
5. 발생 가능한 예외
6. 기본 사용법을 보여주는 최소 예제

```python
def render_cookiecutter_template(
    template_path: Path,
    output_dir: Path,
    context: dict[str, str],
) -> Path:
    """Render a cookiecutter template to output directory.

    Args:
        template_path: Path to cookiecutter template directory.
        output_dir: Where to render the template.
        context: Template variables for cookiecutter.

    Returns:
        Path to the rendered project directory.

    Raises:
        CookiecutterError: If template rendering fails.
    """
    # implementation
```

### 코드 스타일

자동화: [ruff](https://docs.astral.sh/ruff/)를 사용하여 포매팅 및 린팅을 자동으로 진행합니다.

표준:
- 설명적인 변수 이름
- 복잡한 함수는 분할하세요 (20줄 미만으로 줄이는 것을 목표로 하세요)
- 코드베이스에 있는 기존 패턴을 따르세요

### 커밋 컨벤션

**Conventional Commits 권장:**

```
type(scope): subject

feat(cli): add --output option to cast command
fix(scaffold): correct base_node import path
docs(readme): update installation instructions
refactor(utils): simplify name variant conversion
test(cli): add test for path resolution
ci(workflow): update ruff configuration
chore(deps): upgrade dependencies
```

**허용된 type**: `feat`, `fix`, `docs`, `refactor`, `test`, `build`, `ci`, `chore`

**허용된 scope** ([pr_lint.yml](.github/workflows/pr_lint.yml) 참조):
- `cli`, `scaffold`, `utils`, `docs`, `tests`
- `workflow`, `cookiecutter`, `ci`, `deps`

---

## 테스트 작성

### 단위 테스트

**위치** : `tests/unit/`

**대상**: 개별 함수/메서드

**요구 사항**:
- 예외적인 경우를 포함하여 모든 코드 경로를 테스트하십시오.
- 외부 종속성에 대해서는 목업 객체를 사용하세요.

### 통합 테스트

모든 코드 변경에 통합 테스트가 필수는 아니지만, 코드 리뷰 과정에서 필요 시 별도로 요청될 수 있습니다.

**위치**: `tests/integration/`

**대상**: 전체 워크플로우

**요구 사항**:
- 자격 증명을 사용할 수 없는 경우 정상적으로 건너뛰도록 합니다

### pytest 실행

```bash
# 전체 테스트
uv run pytest

# 특정 파일
uv run pytest tests/unit/test_cli.py

# 상세 출력
uv run pytest -v

# 커버리지 (선택)
uv run pytest --cov=act_operator
```

---

## LLM을 활용한 기여

Proact0는 AI 네이티브 개발을 지향합니다. Claude Code, Codex, Cursor, Windsurf, GitHub Copilot 등 LLM 도구를 **협업 파트너**로 활용하는 것을 환영합니다.

### ✅ 권장 활용

- **코드 리뷰**: 작성한 코드의 품질 검토, 리팩토링 제안
- **문서 초안**: 구조화, 표현 개선 (직접 검토 후 수정)
- **테스트 생성**: 시나리오 아이디어, 엣지 케이스 발견
- **디버깅**: 에러 분석, 해결 방법 탐색

### ⚠️ 필수 확인 사항

**LLM 출력을 그대로 제출하지 마세요.** 다음을 반드시 검증하세요:

1. **맥락적 관련성** (Contextual Relevance)
   - Act Operator의 구조와 패턴에 맞는가?
   - 프로젝트 설계 원칙을 이해하는가?

2. **정확성** (Accuracy)
   - 기술적으로 정확한가?
   - 최신 의존성과 호환되는가?

3. **품질** (Quality)
   - 코드 스타일 및 컨벤션 준수하는가?
   - 충분히 이해하고 설명할 수 있는가?

### ❌ 지양사항

- 코드, 문서, PR 설명을 **모두 LLM으로만 생성**
- 생성된 내용을 이해하지 못한 채 제출
- 프로젝트 맥락 없이 일반 패턴만 적용

**품질 미달 PR/이슈는 메인테이너 리소스 보호를 위해 종료될 수 있습니다.**

---

## 하위 호환성 정책

### 🔴 Breaking Change 금지

다음 변경은 **메인테이너 승인 없이 금지**됩니다:

- **CLI API 변경**: 기존 옵션 제거/이름 변경/동작 변경
- **스캐폴드 구조 변경**: 디렉토리 구조, 베이스 클래스 시그니처, 템플릿 파일 제거
- **공개 API 변경**: 함수 시그니처, 반환 타입 변경

### 🟡 신중한 변경

다음 변경은 **충분한 논의 필요**:

- 새 의존성 추가
- Python 버전 요구사항 변경
- 스캐폴드 템플릿 파일 추가/수정

### 🟢 안전한 변경

다음은 자유롭게 변경 가능:

- 버그 수정 (기존 동작 복구)
- 문서 개선
- 내부 리팩토링 (public API 유지)
- 새 옵션 추가 (기존 동작 유지)
- 테스트 추가

### 변경 시 고려사항

**스캐폴드 템플릿 변경 시:**
- 기존 사용자의 프로젝트에 영향을 주지 않는가?
- 마이그레이션 가이드가 필요한가?
- 버전별 템플릿 관리가 필요한가?

**CLI 변경 시:**
- 자동화 스크립트에 영향을 주지 않는가?
- CI/CD 파이프라인에서 사용 중이지 않은가?

---

## PR 및 코드 리뷰

### PR 체크리스트

PR 제출 전 확인하세요:

**필수:**
- [ ] **이슈 연결**: 관련 이슈 링크 (Fixes #123)
- [ ] **설명 작성**: 문제/동기/해결/대안 기술
- [ ] **린트 통과**: `uv run ruff check .`
- [ ] **테스트 통과**: `uv run pytest` (테스트 존재 시)
- [ ] **문서 업데이트**: 사용자 영향이 있다면
- [ ] **하위 호환성**: Breaking change 없음 확인
- [ ] **커밋 메시지**: Conventional Commits 형식

**코드 품질:**
- [ ] 타입 힌트 추가
- [ ] 독스트링 작성 (public API)
- [ ] 작고 명확한 변경

**Skill PR 추가:**
- [ ] Frontmatter 포함
- [ ] "Use this skill when:" 섹션
- [ ] 구조화된 내용 및 예제

### 코드 리뷰 프로세스

**리뷰 타임라인:**
- **초기 응답**: 48시간 내 (영업일 기준)
- **최종 리뷰**: 7일 내 (복잡도에 따라 변동)
- **No response 시**: 디스코드에서 리마인드

**리뷰어 기대사항:**
- 건설적 피드백 제공
- 코드 품질, 테스트, 문서 검토
- 하위 호환성 영향 검토

**기여자 기대사항:**
- 피드백에 신속히 응답
- 요청된 변경사항 반영
- CI/CD 통과 유지

---

## 버전 및 릴리즈

### 버전 관리

- **버전 위치**: `act_operator/__init__.py`
- **관리 도구**: hatch
- **정책**: 기여자는 버전을 직접 변경하지 않습니다. 메인테이너가 릴리즈 시 관리합니다.

### 의존성 자동 업그레이드

- **자동화**: 매주 일요일 자정에 `uv lock --upgrade` 실행 ([uv_lock_upgrade.yml](.github/workflows/uv_lock_upgrade.yml))
- **PR 생성**: 변경사항이 있으면 자동으로 PR 생성
- **기여자 액션**: 자동 생성된 의존성 PR 리뷰 및 승인 가능

### 보안 취약점 보고

**보고 방법:**
- **채널**: [GitHub Security Advisories](https://github.com/Proact0/Act-Operator/security/advisories)
- **필수 정보**:
  - 재현 절차 (단계별 상세 설명)
  - 영향 범위 (영향 받는 버전, 기능)
  - 우회 방안 (가능한 경우)

---

## 도움 받기

저희 목표는 최대한 접근하기 쉬운 개발자 환경을 구축하는 것입니다. 설정 과정에서 어려움을 겪으시는 경우, [Discord](https://discord.gg/4GTNbEy5EB)에서 직접 문의하시거나 커뮤니티 구성원의 도움을 받으세요.

> [!NOTE]
> 이제 Proact0에 여러분의 뛰어난 코드를 기여할 준비가 되셨습니다!

---

<div align="center">
  <p>건설적인 피드백과 협업을 환영합니다.</p>
  <p>감사합니다! 🙏</p>
</div>
