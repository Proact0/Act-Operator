name: "✨ 기능 요청 (KR)"
description: Act Operator CLI에 대한 새로운 기능 또는 개선 사항을 제안해주세요.
labels: [pending, enhancement]
body:
  - type: markdown
    attributes:
      value: |
        Act Operator 개선 아이디어를 공유해주셔서 감사합니다!

        이 폼은 Act Operator( LangGraph 기반 “Act” 블루프린트를 스캐폴딩하는 CLI )의 **기능 제안/개선 요청**을 위한 것입니다.
        일반 질문이나 논의는 디스코드를 이용해주세요.

        제출 전, 유사한 요청이 이미 있는지 아래 리소스를 확인해주세요:

        * Act Operator README: https://github.com/Proact0/Act-Operator#readme
        * Act Operator GitHub Issues: https://github.com/Proact0/Act-Operator/issues
        * 리포지토리 검색: https://github.com/Proact0/Act-Operator
        * Proact0 디스코드: https://discord.gg/4GTNbEy5EB
  - type: checkboxes
    id: checks
    attributes:
      label: 리소스 확인 여부
      description: 제출 전에 다음 항목을 확인해주세요.
      options:
        - label: 이 이슈는 Act Operator CLI의 기능/개선 요청이며, 버그 리포트가 아닙니다.
          required: true
        - label: 제안을 요약하는 명확하고 간결한 제목을 작성했습니다.
          required: true
        - label: 기존 이슈/PR을 검색했고, 중복되지 않습니다.
          required: true
  - type: textarea
    id: description
    validations:
      required: true
    attributes:
      label: 요약
      description: |
        어떤 기능/개선을 원하시나요?
        동기/목표/사용자에게 주는 이점을 설명해주세요.
      placeholder: |
        * Y를 지원하기 위해 X 추가를 제안합니다.
        * Z 방식으로 사용자에게 도움이 됩니다.
  - type: textarea
    id: use-case
    validations:
      required: true
    attributes:
      label: 사용 사례 / 시나리오
      description: 이 기능이 유용한 대표 워크플로우/상황을 설명해주세요.
      placeholder: |
        * 스캐폴딩 시 ..., ...이 필요합니다.
        * 캐스트 추가 시 ..., ...가 있으면 좋겠습니다.
  - type: textarea
    id: proposal
    validations:
      required: false
    attributes:
      label: 제안 솔루션 / UX
      description: |
        CLI 플래그, 프롬프트, 설정, 예시 명령에 대한 아이디어가 있다면 작성해주세요.
      placeholder: |
        예시 CLI:
        uv run act new --path ./my-act --act-name "My Act" --cast-name "Main Cast" --flag ...
  - type: textarea
    id: alternatives
    validations:
      required: false
    attributes:
      label: 고려한 대안
      description: 가능하다면, 다른 접근과 트레이드오프를 설명해주세요.
  - type: textarea
    id: references
    validations:
      required: false
    attributes:
      label: 참고자료(선택)
      description: 관련 이슈/PR/문서 링크를 추가해주세요.
  - type: textarea
    id: screenshots
    validations:
      required: false
    attributes:
      label: 목업 / 예시(선택)
      description: 해당되는 경우 제안을 이해하는 데 도움이 되는 스크린샷이나 의사 출력(pseudo-output)을 추가해주세요.
  - type: textarea
    id: additional
    validations:
      required: false
    attributes:
      label: 추가 컨텍스트
      description: 기타 고려 사항이나 배경이 있으면 작성해주세요.
  - type: markdown
    attributes:
      value: |
        브랜치 팁: 작업을 시작할 때 `feat/[간결한-기능-이름]` 브랜치를 만들어주세요.
        PR은 작고 집중된 변경으로 유지해주세요.
