## 컨트리뷰팅 가이드

- 영어로 읽기: [CONTRIBUTING_EN.md](CONTRIBUTING_EN.md)

Act Operator 오픈소스 프로젝트에 관심 가져주셔서 감사합니다! 버그 리포트, 문서 개선, 테스트 추가, 기능 제안/구현 등 **모든 형태의 기여**를 환영합니다. 작고 명확한 변경과 친절한 설명, 충분한 테스트가 좋은 협업을 만듭니다.

## 기여 유형
- **버그 리포트**: 재현 절차/환경/예상 동작/실제 동작을 포함해 이슈 템플릿으로 등록
- **문서 개선**: Claude Skills/README/가이드/예제 보완, 오탈자/표현 개선
- **테스트 보강**: 신규/변경 기능에 대한 단위/통합 테스트 추가
- **기능 제안/구현**: 작은 단위로 나눠 명확한 PR로 제안/구현
- **개발자 경험/성능 개선**: 린팅/타입/빌드/실행 흐름 최적화

## 빠른 시작

### 요구사항
- **Python 3.11+**
- **Windows, macOS, Linux** 모두 지원
- **uv**(권장): 의존성/실행/빌드를 간결하게 관리합니다.

설치 안내: `uv` 공식 문서를 참고하세요.
- 설치 가이드: https://docs.astral.sh/uv/getting-started/installation/

```bash
# uv 설치
pip install uv
```

### 리포지토리 클론 및 개발 환경 구성
```bash
# 리포지토리 클론
git clone https://github.com/Proact0/Act-Operator.git
cd act-operator

# 개발 및 테스트 의존성 설치
uv sync --dev
```

### 로컬에서 테스트/실행
```bash
# 전체 테스트 실행
uv run pytest

# CLI 사용 예시: 새 Act 프로젝트 생성
uv run act new

# CLI 사용 예시: 기존 프로젝트에 Cast 추가
uv run act cast

# 빌드 산출물 생성 (배포 전 점검용)
uv build
```

## 작업 흐름 및 원칙
- **작게, 명확하게**: 변경 범위는 작고 목적은 분명하게 유지합니다.
- **이슈 우선**: 가능하면 이슈를 먼저 만들고 배경/문제/목표를 정리합니다.
- **브랜치 전략**: 기능/수정마다 별도 브랜치로 작업합니다.
  - 예: `feat/add-cast-validation`, `fix/cli-prompt-edge-case`
- **커밋 컨벤션(권장: Conventional Commits)**
  - 형식: `type(scope): subject`
  - 타입 예: `feat`, `fix`, `docs`, `refactor`, `test`, `build`, `ci`, `chore`
  - 예시:
    ```text
    feat(cli): add --act-name default from custom path
    fix(scaffold): normalize cast directory to snake_case
    docs(readme): clarify Python version requirement to 3.12+
    ```

## 코드 스타일, 타입, 품질
본 프로젝트는 `ruff`, `pytest`를 사용합니다.

### 린트(ruff)
`pyproject.toml` 설정에 따라 일반 오류(E/F), import(I), Bugbear(B)를 확인합니다. 길이 제한(E501)은 제외되지만, 가독성을 위해 적절히 줄바꿈을 권장합니다.

```bash
# 코드 린트 검사
uv run ruff check .

# 선택: 포맷 적용 (원치 않으면 생략)
uv run ruff format .
```

참고: `act_operator/scaffold` 경로는 린트 대상에서 제외됩니다.

### 테스트(pytest)
테스트는 `tests/` 하위에 통합/단위 테스트로 구성되어 있습니다. 새 기능/수정 사항에는 적절한 테스트를 추가하세요.

```bash
uv run pytest -q
```

## 문서/예제 업데이트
- 사용자에 영향이 있는 변경은 `README.md` 또는 관련 가이드를 함께 업데이트합니다.
- 스캐폴드 템플릿(`act_operator/act_operator/scaffold/`)의 `README.md`/`TEMPLATE_README.md`도 변경 반영이 필요한지 확인합니다.

## Claude Agent Skill 기여

Act Operator 스캐폴드에는 Claude Agent가 Cast 개발을 지원하기 위한 Skill들이 포함되어 있습니다. 이 Skill들을 개선하거나 새로운 Skill을 추가하는 방법을 안내합니다.

### Skill 구조

각 Skill은 다음 디렉터리 구조를 따릅니다:

```
.claude/skills/<skill-name>/
├── SKILL.md          # Skill 메인 문서 (필수)
├── references/       # 참조 문서들 (선택)
│   └── *.md
├── scripts/          # 유틸리티 스크립트들 (선택)
│   └── *.py
└── assets/           # 예제 파일들 (선택)
    └── *.txt, *.py, etc.
```

### 기존 Skill 개선

**SKILL.md 작성 가이드:**
- **Frontmatter 필수**: YAML frontmatter에 `name`과 `description` 포함
  ```yaml
  ---
  name: skill-name
  description: 명확하고 간결한 설명 - 언제 이 skill을 사용해야 하는지 포함
  ---
  ```
- **명확한 사용 시점**: "Use this skill when:" 섹션으로 사용 시나리오 명시
- **구조화된 내용**: Workflow/Task/Reference 패턴 중 적합한 구조 선택
- **실용적인 예제**: 코드 샘플, 체크리스트, 단계별 가이드 포함
- **참조 연결**: 관련 `references/`, `scripts/`, `assets/` 파일 언급

**references/ 문서:**
- API 레퍼런스, 베스트 프랙티스, 패턴 가이드 등
- Markdown 형식으로 작성
- Skill의 메인 문서에서 적절히 링크

**scripts/ 유틸리티:**
- 검증, 자동화, 헬퍼 스크립트 등
- Python 스크립트 권장
- 독립 실행 가능하거나 Skill 컨텍스트에서 사용 가능해야 함

**assets/ 예제:**
- 템플릿, 설정 파일, 예제 코드 등
- Skill 문서에서 참조되는 실제 사용 가능한 예제

### 새 Skill 추가

1. **Skill 디렉터리 생성**
   ```bash
   mkdir -p act_operator/act_operator/scaffold/{{ cookiecutter.act_slug }}/.claude/skills/<skill-name>/{references,scripts,assets}
   ```

2. **SKILL.md 작성**
   - 기존 Skill들(`cast-development`, `act-setup` 등)을 참고하여 구조 작성
   - Frontmatter에 명확한 name과 description 포함
   - 사용 시점, 워크플로우, 예제 포함

3. **필요한 리소스 추가**
   - `references/`: 관련 문서
   - `scripts/`: 유틸리티 스크립트
   - `assets/`: 예제 파일

4. **테스트 및 검증**
   - Skill이 실제 Claude Agent에서 올바르게 작동하는지 확인
   - 문서의 예제들이 정확한지 검증

### Skill 기여 체크리스트

- [ ] SKILL.md에 frontmatter(`name`, `description`) 포함
- [ ] "Use this skill when:" 섹션으로 사용 시점 명확히 기술
- [ ] 구조화된 내용(Workflow/Task/Reference 등)
- [ ] 실용적인 예제 및 코드 샘플 포함
- [ ] 관련 references/scripts/assets 파일과 연결
- [ ] 기존 Skill들과 일관된 스타일 유지
- [ ] 문서 내 링크 및 참조가 정확한지 확인

### 기존 Skill 목록

현재 포함된 Skill들:
- **cast-development**: Cast 모듈 개발 (노드, 상태, 그래프 구현)
- **act-setup**: Act 프로젝트 설정 및 uv 워크스페이스 관리
- **graph-composition**: 그래프 구성 및 엣지 연결
- **modules-integration**: 모듈 통합 (agents, tools, prompts 등)
- **node-implementation**: 노드 구현 패턴 및 베스트 프랙티스
- **state-management**: 상태 관리 및 스키마 정의
- **testing-debugging**: 테스트 작성 및 디버깅

새로운 Skill 추가 시 이 목록도 업데이트해주세요.

## 이슈 템플릿 사용
- `.github/ISSUE_TEMPLATE`에 제공된 템플릿을 사용하세요.
  - **Backlog**: 기능 제안/백로그 산정/작업 단계 정의
  - **Bug Report**: 프로그래머 기원 버그(예: 널 포인터, 경계 오류, 누수 등)

## PR 체크리스트
- 설명: 문제/동기/해결/대안/리스크를 간결히 기술
- 테스트: 새 테스트 추가 또는 기존 테스트 통과 여부 명시
- 품질: `uv run ruff check .`, `uv run pytest` **모두 통과**
- 문서: 사용자 영향이 있다면 문서 업데이트 포함
- 범위: 검토하기 쉬울 만큼 **작고 명확**하게 유지

## CLI 개발 팁
- 엔트리포인트: `pyproject.toml`의 `[project.scripts]`
  - `act` → `act_operator.cli:main`
- 로컬 실행: `uv run act ...`
- 모듈 진입: 필요 시 `uv run -m act_operator`

## 버전 및 릴리즈 정책
- 버전은 `hatch`로 관리하며, 정의 위치는 `act_operator/__init__.py`입니다.
- **기여자는 버전을 직접 올리지 않습니다.** 릴리즈 시점의 버전 증분과 배포(`uv build`)는 메인테이너가 수행합니다.

## 보안 취약점 보고
- 공개 이슈 대신 **비공개 채널**(예: GitHub Security Advisories)을 활용해 보고하는 것을 권장합니다.
- 재현 가능성/영향 범위/우회 방안이 있으면 함께 제공해주세요.

## 라이선스
- 본 프로젝트는 **Apache-2.0** 라이선스를 따릅니다. 프로젝트에 기여하는 코드는 동일 라이선스 하에 제공됩니다.

## 커뮤니티/질문
- 기여와 관련된 질문은 디스코드에 남겨주세요: https://discord.gg/4GTNbEy5EB
- 건설적인 피드백과 협업을 환영합니다.