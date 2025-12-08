name: "🐛 버그 리포트 (KR)"
description: Act Operator CLI의 버그를 신고해주세요. 보안 이슈는 GitHub Security Advisories(보안 탭)를 사용해주세요. 사용 관련 질문은 디스코드를 이용해주세요.
labels: [pending, bug]
body:
  - type: markdown
    attributes:
      value: |
        버그 리포트를 작성해주셔서 감사합니다.

        이 폼은 Act Operator( LangGraph 기반 “Act - AX Template” 블루프린트를 스캐폴딩하는 CLI )의 **버그**를 신고하기 위한 것입니다.
        사용 방법 문의, 기능 요청, 일반적인 설계 질문은 디스코드를 이용해주세요.

        버그 등록 전, 아래 리소스를 확인하여 이미 보고되었거나 해결된 이슈인지 확인해주세요:

        * Act Operator README: https://github.com/Proact0/Act-Operator#readme
        * Act Operator GitHub Issues: https://github.com/Proact0/Act-Operator/issues
        * 리포지토리 검색: https://github.com/Proact0/Act-Operator
        * uv 문서: https://docs.astral.sh/uv/
        * Proact0 디스코드: https://discord.gg/4GTNbEy5EB
  - type: checkboxes
    id: checks
    attributes:
      label: 리소스 확인 여부
      description: 제출 전에 다음 항목을 확인해주세요.
      options:
        - label: 이 이슈는 Act Operator CLI의 버그이며, 사용 질문이 아닙니다. 질문은 디스코드 (https://discord.gg/4GTNbEy5EB)를 이용해주세요.
          required: true
        - label: 이슈를 요약하는 명확하고 간결한 제목을 작성했습니다.
          required: true
        - label: 최소 재현 예제(minimal reproducible example)가 무엇인지 읽었습니다 (https://stackoverflow.com/help/minimal-reproducible-example).
          required: true
        - label: 사용한 정확한 CLI 명령 또는 코드 포함하여, 자체 포함된 최소 재현 단계를 포함했습니다.
          required: true
  - type: textarea
    id: reproduction
    validations:
      required: true
    attributes:
      label: 재현 단계 및 예시 명령
      description: |
        정확한 단계와 명령이 포함된 자체 포함 최소 재현을 작성해주세요.
        아래 예시는 본인의 사례로 교체해주세요!
      placeholder: |
        # 단계
        1. 다음 명령을 실행합니다

        # 예시 명령
        uv run act new --act-name "Demo Act" --cast-name "Main Cast"
        uv run act cast --path ./demo-act --cast-name "Support Cast"

        # 관찰된 동작
        - 발생한 현상을 작성

        # 기대 동작
        - 기대한 동작을 작성
      render: shell
  - type: textarea
    id: error
    validations:
      required: false
    attributes:
      label: 오류 메시지 및 스택 트레이스(해당 시)
      description: |
        오류를 신고하는 경우, 전체 오류 메시지와 스택 트레이스를 포함해주세요.
      placeholder: |
        예외 + 전체 스택 트레이스
      render: shell
  - type: textarea
    id: description
    validations:
      required: true
    attributes:
      label: 설명
      description: |
        문제를 설명해주세요.
        무엇을 하려 했는지, 기대한 동작, 실제 동작을 간단히 작성합니다.
      placeholder: |
        * Act Operator CLI로 X를 스캐폴딩하려고 합니다.
        * Y가 나타나길 기대했습니다.
        * 대신 Z가 발생합니다.
  - type: textarea
    id: screenshots
    validations:
      required: false
    attributes:
      label: 스크린샷(선택)
      description: 해당되는 경우, 문제 설명에 도움이 되는 스크린샷을 추가해주세요.
  - type: textarea
    id: system-info
    attributes:
      label: 시스템 정보
      description: |
        아래 정보를 제공해주세요. 관련된 경우 명령 출력 결과를 붙여넣어 주세요.
      placeholder: |
        OS: Windows/macOS/Linux + 버전
        Python: `python --version` 출력
        uv: `uv --version` 출력
        Act Operator 버전: `python -c "import act_operator; print(getattr(act_operator, '__version__', 'unknown'))"` 출력
        설치 방법: uv/pip/pipx/기타
        가상환경: 사용 여부(도구명 포함)
    validations:
      required: true
