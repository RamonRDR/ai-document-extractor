<div align="center">

# AI Document Extractor 📄

**Extraia dados estruturados de documentos financeiros, valide os valores e exporte com revisão humana.**

[🇺🇸 English](README.md) · [🇧🇷 Português](README.pt-BR.md) · [🇪🇸 Español](README.es.md)

<!-- BADGES:START -->
[![CI](https://github.com/RamonRDR/ai-document-extractor/actions/workflows/ci.yml/badge.svg?branch=feat%2Fdocument-extractor-full-implementation)](https://github.com/RamonRDR/ai-document-extractor/actions/workflows/ci.yml?query=branch%3Afeat%2Fdocument-extractor-full-implementation)
![Python 3.14](https://img.shields.io/badge/Python-3.14-3776AB)
[![MIT License](https://img.shields.io/badge/License-MIT-2ea44f)](LICENSE)

![FastAPI >=0.128](https://img.shields.io/badge/FastAPI-0.128%2B-009688)
![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-E92063)
![Uvicorn ASGI](https://img.shields.io/badge/Uvicorn-ASGI-4051B5)
![httpx >=0.28](https://img.shields.io/badge/httpx-0.28%2B-4479A1)
![Pillow >=11.3](https://img.shields.io/badge/Pillow-11.3%2B-5C5C5C)
![pypdfium2 >=5.14](https://img.shields.io/badge/pypdfium2-5.14%2B-6D3A88)
![python-multipart >=0.0.20](https://img.shields.io/badge/python--multipart-0.0.20%2B-6A5ACD)
![Docker Build](https://img.shields.io/badge/Docker-build%20validated-2496ED)

![OpenAI API optional](https://img.shields.io/badge/OpenAI%20API-opt--in%20adapter-5A6872)
![Structured outputs](https://img.shields.io/badge/Structured%20Outputs-JSON%20Schema-7E57C2)

![pytest 77 passing](https://img.shields.io/badge/pytest-77%20passing-0A9EDC)
![pytest-asyncio](https://img.shields.io/badge/pytest--asyncio-enabled-0A9EDC)
![Ruff lint and format](https://img.shields.io/badge/Ruff-lint%20%26%20format-D7FF64)
![mypy type checked](https://img.shields.io/badge/mypy-type%20checked-2A6DB4)
![OpenAPI documented](https://img.shields.io/badge/OpenAPI-%2Fdocs%20validated-6BA539)
![30 synthetic fixtures](https://img.shields.io/badge/Synthetic%20Evaluation-30%20fixtures-607D8B)
![Package build](https://img.shields.io/badge/Package%20Build-wheel%20%2B%20sdist-455A64)
[![Feature branch formatting](https://github.com/RamonRDR/ai-document-extractor/actions/workflows/format-branch.yml/badge.svg?branch=feat%2Fdocument-extractor-full-implementation)](https://github.com/RamonRDR/ai-document-extractor/actions/workflows/format-branch.yml?query=branch%3Afeat%2Fdocument-extractor-full-implementation)

<!-- BADGES:END -->

</div>

> **Estado do projeto:** implementação no [PR #1](https://github.com/RamonRDR/ai-document-extractor/pull/1), com os seis apontamentos iniciais do Codex corrigidos na branch; aguardando revisão complementar e autorização para merge. O [CI da branch de desenvolvimento](https://github.com/RamonRDR/ai-document-extractor/actions/workflows/ci.yml?query=branch%3Afeat%2Fdocument-extractor-full-implementation) está verde. Sem deploy ou pacote publicado.

## Visão geral

API sem persistência para documentos financeiros de página única, com revisão humana. Recebe PDF, PNG ou JPEG, estrutura campos financeiros, verifica consistência aritmética e exige confirmação antes da exportação CSV/JSON. Demonstra backend Python, automação financeira, contratos REST tipados, arquitetura de adaptadores multimodais e CI hospedado para um portfólio internacional.

**Dois modos diferentes:** `demo` retorna **sempre o mesmo registro fictício** para qualquer entrada válida; **não** faz OCR nem extração por IA. `openai` é um adaptador multimodal **opcional** implementado; a extração real com API paga **ainda não foi executada ou avaliada**.

## Funcionalidades implementadas

- PDF, PNG e JPEG de página única; validação de assinatura/MIME, tamanho de upload, renderização de PDF, verificação de imagem e limite de pixels.
- Interface de provedor substituível, demonstração determinística fictícia e adaptador multimodal opcional da OpenAI com saída estruturada por JSON Schema.
- Contratos Pydantic v2 com campos nulos, proveniência (`extracted`, `inferred`, `missing` ou `demo`), tempos e avisos.
- Validação de CNPJ, datas, valores `Decimal`, totais dos itens, subtotal, descontos, impostos e acréscimos.
- Interface web simples de correção/confirmação; resultado original separado do corrigido na resposta.
- Exportação CSV e JSON após confirmação humana; proteção contra fórmulas maliciosas no CSV.
- Processamento em lote de até cinco arquivos por padrão, erros individuais e contadores.
- 30 documentos sintéticos, testes de modelo simulados, verificação de empacotamento e automação no GitHub Actions.

## Stack tecnológica

| Camada | Implementação real |
| --- | --- |
| Execução | **Python 3.14**, pacote versão `0.1.0` |
| API e dados | FastAPI **0.128+** (mínimo declarado), Pydantic **v2** (2.11+), Uvicorn ASGI, python-multipart **0.0.20+** |
| Documentos e HTTP | pypdfium2 **5.14+** para PDF, Pillow **11.3+** para imagens, httpx **0.28+** para requisições ao provedor |
| Limite de IA | Adaptador OpenAI API com imagens multimodais e saída estruturada JSON Schema, desativado por padrão; extração externa real não validada |
| Qualidade | pytest, pytest-asyncio, Ruff lint/formatação, mypy estrito, 30 casos de avaliação sintética determinística |
| Automação | GitHub Actions, build wheel/sdist com Hatchling, build Docker, formatação em branch de recurso |

Números com `+` representam **versões mínimas declaradas**, não versões exatas fixadas. O manifesto permite atualizações compatíveis. Não utilizamos banco de dados, Redis, Alembic, Docker Compose, RAG, embeddings ou MCP.

## Arquitetura

Fluxo: **upload → validação → preparação PDF/imagem → provedor selecionado → contrato Pydantic → verificações financeiras → correção humana → exportação confirmada**. Não há banco nem armazenamento de documentos. Veja o [diagrama](docs/architecture.md), a [documentação dos schemas](docs/schema.md) e a [ADR do provedor/renderizador](docs/adr/0001-provider-and-renderer.md).

## Pré-requisitos

Python **3.14** e pip. Docker Engine é opcional. Não é necessária chave de IA para demo, testes ou CI. Não utilize documentos privados em demonstrações públicas.

## Instalação

~~~bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
~~~

No Windows, ative com `.venv\Scripts\activate`. Build opcional do contêiner: `docker build -t ai-document-extractor .`.

## Configuração

Consulte [`.env.example`](.env.example). Trata-se de um exemplo: a aplicação lê **variáveis de ambiente** e não carrega o arquivo automaticamente.

| Variável | Finalidade |
| --- | --- |
| `ALLOW_PAID_AI` | Padrão `0`; deve ser `1` para modo real |
| `OPENAI_API_KEY` | Segredo para extração real autorizada; nunca versionar |
| `AI_MODEL` | Padrão `gpt-4o-mini` (modelo configurado, não resultado de validação real) |
| `AI_TIMEOUT_SECONDS` | Timeout do provedor (padrão 20 segundos) |
| `MAX_UPLOAD_BYTES` | Limite por arquivo (padrão 5.242.880 bytes) |
| `MAX_BATCH_FILES` | Limite de arquivos por requisição (padrão 5) |
| `EVAL_LIVE` | Autorização adicional para avaliação real manual, padrão `0` |
| `AI_INPUT_USD_PER_MILLION` / `AI_OUTPUT_USD_PER_MILLION` | Tarifas informadas pelo usuário para **estimativa**, não limite de cobrança |

O CI não usa segredos. A extração real pode gerar custos e transmite a imagem do documento ao provedor.

## Execução e interface

~~~bash
uvicorn document_extractor.api:app --reload
# Alternativa Docker:
docker run --rm -p 8000:8000 ai-document-extractor
~~~

A interface web local fica em `http://127.0.0.1:8000/`. Endpoints REST:

| Endpoint | Função |
| --- | --- |
| `GET /health` | Estado básico |
| `GET /docs` | Swagger UI e documentação automática do FastAPI |
| `GET /openapi.json` | Schema OpenAPI |
| `POST /api/v1/extract` | Um arquivo, `mode=demo` ou `mode=openai` |
| `POST /api/v1/batch` | Múltiplos arquivos com resultados independentes |
| `POST /api/v1/review` | Resultado original, campos corrigidos e confirmação |
| `POST /api/v1/export/csv` / `POST /api/v1/export/json` | Download dos dados revisados e confirmados |

## Exemplo de utilização

~~~bash
curl -X POST http://127.0.0.1:8000/api/v1/extract \
  -F "file=@recibo-ficticio.png;type=image/png" \
  -F "mode=demo"
~~~

Resposta abreviada **fictícia**, não extraída da imagem:

~~~json
{
  "mode": "demo",
  "document": {
    "document_type": "synthetic_receipt",
    "issuer_name": "Example Studio (FICTIONAL)",
    "issuer_cnpj": null,
    "issue_date": "2026-01-15",
    "total": "140.00",
    "items": [{"description": "Synthetic service", "quantity": "2", "unit_price": "75.00", "total": "150.00"}]
  },
  "needs_review": true,
  "notice": "DEMO ONLY: fixed fictional data. No AI extraction or OCR performed."
}
~~~

A resposta completa inclui moeda, número, subtotal/ajustes, proveniência, avisos e duração. [Detalhes do schema](docs/schema.md).

## Validação financeira e revisão humana

CNPJ (formato e dígitos), datas, valores, quantidades, multiplicação dos itens e conciliação de subtotal/ajustes geram avisos, sem substituir silenciosamente valores. Campos ausentes são nulos, sem invenções. Envie `{"original": <resultado-extração>, "corrected": <documento-editado>, "confirmed": true}` para `POST /api/v1/review`; depois envie a resposta a `/api/v1/export/csv` ou `/api/v1/export/json`. Sem confirmação, a exportação retorna **HTTP 409**. A interface web implementa esse fluxo.

## Processamento em lote

Envie vários campos multipart `files` para `POST /api/v1/batch`; cada entrada contém índice, sucesso, resultado ou erro. Os totais diferenciam acertos e falhas. O limite padrão é cinco documentos, com tamanho máximo individual.

## Testes automatizados e avaliação

~~~bash
ruff check .
ruff format --check .
mypy --ignore-missing-imports src/document_extractor
pytest -q
python -m evaluation.runner --mode fixture --report evaluation-report.json
python -m build
~~~

A suíte agora reúne **77 casos de teste**, incluindo proteção na estimativa de custos e tratamento de PNGs corrompidos sem interromper o lote. O [workflow de CI](https://github.com/RamonRDR/ai-document-extractor/actions/workflows/ci.yml?query=branch%3Afeat%2Fdocument-extractor-full-implementation) executa os testes e valida automaticamente a contagem exibida no badge com o relatório JUnit. A [execução anterior com 61 testes](https://github.com/RamonRDR/ai-document-extractor/actions/runs/42741844565) precede as correções adicionais. As 30 fixtures fictícias cobrem arquivos, schemas e regras financeiras; **não** medem acurácia de extração de IA nem custo real. A avaliação paga é manual, exigindo `EVAL_LIVE=1`, `ALLOW_PAID_AI=1`, chave e orçamento explícito não nulo. Somente com **orçamento já autorizado**, o comando segue o formato `python -m evaluation.runner --mode live --max-documents 3 --max-usd-per-document 0.20 --budget-usd 0.60`. Os parâmetros são reserva estimada, **não** limite de cobrança do provedor.

## GitHub Actions e manutenção dos badges

O [workflow de CI](.github/workflows/ci.yml) executa Ruff, formatação, mypy, pytest, validação de schema, fixtures determinísticas, build wheel/sdist e job separado de Docker. O [formatador de branch](.github/workflows/format-branch.yml) normaliza arquivos somente em branches `feat/**`, sem comitar na `main`. O CI usa runners hospedados e **nunca executa modelos pagos**.

O **badge pytest é estático e auditável**: [`scripts/check_readme_badges.py`](scripts/check_readme_badges.py) compara o número aprovado com o relatório JUnit XML real e verifica os três READMEs. Alterações nos testes exigem atualização das três cópias e CI verde. Os badges dinâmicos CI/formatação apontam à branch de desenvolvimento enquanto o PR #1 estiver aberto; após merge, os links devem apontar à `main`. [Inventário dos badges](docs/badges.md).

## Segurança e privacidade

Conteúdo de documentos é entrada não confiável; nenhuma instrução extraída vira comando executável. Validação de formato/MIME, páginas, bytes/pixels, timeout e prevenção de fórmulas no CSV reduzem riscos. A aplicação não armazena documentos de forma definitiva, mas o parser multipart do Starlette pode usar arquivos temporários no disco. Um middleware limita o tamanho total antes do parser; as imagens enviadas ao provedor têm metadados EXIF/GPS eliminados. Nenhum segredo, documento financeiro real, chamada paga ou publicação foi incluído. Consulte o [modelo de privacidade e ameaças](docs/privacy.md).

## Limitações conhecidas e evoluções

Somente uma página; sem autenticação, rate limiting, antivírus, isolamento do parser PDF, persistência, multi-tenant, filas ou evidência visual da origem de cada campo. O modelo opcional ainda não foi avaliado com gabarito real; a conferência humana é indispensável. Produção exigiria isolamento, controle de acesso e avaliação real. O projeto **não está publicado** como sistema contábil.

## Estrutura do repositório

| Caminho | Responsabilidade |
| --- | --- |
| `src/document_extractor/api.py` / `ui.html` | Rotas HTTP e revisão humana |
| `src/document_extractor/documents.py` | Validação e renderização PDF/imagem |
| `src/document_extractor/providers.py` / `prompts.py` | Provedores, JSON Schema e prompt |
| `src/document_extractor/schemas.py` / `validation.py` / `finance.py` | Tipos e regras financeiras |
| `evaluation/` / `tests/` | Avaliação sintética e testes |
| `scripts/check_readme_badges.py` | Consistência dos READMEs com JUnit |
| `.github/workflows/` | CI e formatador de branch |
| `docs/` | Arquitetura, schemas, ADR, privacidade e auditorias |

## Contribuições

Abra issue ou PR descrevendo a proposta; mantenha testes e três idiomas consistentes. Execute Ruff, mypy e pytest antes. Não comite documentos pessoais, tokens ou segredos. O [PR #1](https://github.com/RamonRDR/ai-document-extractor/pull/1) já recebeu Codex Review com seis apontamentos corrigidos e aguarda conferência complementar e merge autorizado.

## Licença

Código da aplicação sob [Licença MIT](LICENSE), copyright 2026 Ramon Rodriguez. Dependências mantêm licenças próprias, inclusive PDFium/pypdfium2. Não há garantia de suporte comercial ou de segurança para produção.
