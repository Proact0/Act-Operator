{% if cookiecutter.language == 'en' %}# Act: {{ cookiecutter.act_name }}

A LangGraph-based Act project scaffolded with Act Operator.

## Quick Start

1. Install dependencies:
   ```bash
   uv sync --all-packages
   ```

2. Run the development server:
   ```bash
   uv run langgraph dev
   ```

3. Access Studio UI:
   - Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
   - API: http://127.0.0.1:2024
   - API Docs: http://127.0.0.1:2024/docs

For detailed documentation, see [TEMPLATE_README.md](TEMPLATE_README.md).
{% else %}# Act: {{ cookiecutter.act_name }}

Act Operator로 스캐폴딩된 LangGraph 기반 Act 프로젝트입니다.

## 빠른 시작

1. 의존성 설치:
   ```bash
   uv sync --all-packages
   ```

2. 개발 서버 실행:
   ```bash
   uv run langgraph dev
   ```

3. Studio UI 접속:
   - Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
   - API: http://127.0.0.1:2024
   - API 문서: http://127.0.0.1:2024/docs

자세한 문서는 [TEMPLATE_README.md](TEMPLATE_README.md)를 참고하세요.
{% endif %}
