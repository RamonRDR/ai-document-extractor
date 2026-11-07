# AI Document Extractor

[English](README.md) · **Português** · [Español](README.es.md)

API Python sem persistência para extração estruturada de documentos financeiros de página única, validação contábil e revisão humana. Demonstra FastAPI, IA multimodal, Pydantic, Decimal, testes e CI.

> **Aviso:** o modo demo retorna sempre um exemplo fixo e fictício, independentemente do arquivo. **Não é OCR nem extração real por IA.** O modo real é opt-in e pode gerar cobrança. Não envie documentos privados a uma demonstração pública.

## Funcionalidades

Upload de PDF, PNG e JPEG com verificação de assinatura, MIME, tamanho, imagem e página única; interface web de revisão em `/`; API `/docs`; modos `demo` e `openai`; JSON estruturado com campos ausentes, proveniência, divergências e revisão humana. Exportação CSV e JSON requer confirmação. Lotes de até cinco arquivos retornam erros por documento.

## Stack e arquitetura

Python 3.14, FastAPI, Pydantic v2, httpx, Pillow, pypdfium2, pytest, Ruff, mypy, Docker e GitHub Actions. A arquitetura isola upload, renderização de PDF, adaptadores de IA, schema, regras financeiras, revisão e exportação. Confira [diagrama](docs/architecture.md), [schemas](docs/schema.md) e [decisões técnicas](docs/adr/0001-provider-and-renderer.md).

## Instalação

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn document_extractor.api:app --reload
```

No Windows, ative `.venv\Scripts\activate`. Abra `http://127.0.0.1:8000/` ou `/docs`. Com Docker: `docker build -t ai-document-extractor .` e `docker run --rm -p 8000:8000 ai-document-extractor`.

## Configuração e upload

Veja [`.env.example`](.env.example). O modo demo não exige chave. Para habilitar uma chamada real manual, configure `ALLOW_PAID_AI=1`, `OPENAI_API_KEY` e envie `mode=openai`; não publique credenciais. O CI não faz chamadas pagas.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/extract \
  -F "file=@recibo-ficticio.png;type=image/png" -F "mode=demo"
```

Trecho da resposta JSON do **exemplo fictício**:

```json
{"mode":"demo","document":{"issuer_name":"Example Studio (FICTIONAL)","total":"140.00","issuer_cnpj":null},"needs_review":true}
```

A resposta real inclui os demais campos (tipo, data, número, moeda, subtotal, descontos, impostos, acréscimos e itens), proveniência, avisos e tempo de processamento. Todos os valores monetários são tratados com `Decimal`.

## Validações e revisão humana

Verificação de dígitos do CNPJ, datas, valores negativos, quantidade, soma dos itens, subtotal, total e ajustes. Campos ausentes continuam nulos, sem valores inventados. A revisão ocorre em `POST /api/v1/review` com `original`, `corrected` e `confirmed: true`. Envie o resultado para `/api/v1/export/csv` ou `/api/v1/export/json`; sem confirmação retorna 409. O resultado original é preservado no JSON, separado das correções.

## Testes, avaliação e GitHub Actions

```bash
ruff check .
ruff format --check .
mypy --ignore-missing-imports src/document_extractor
pytest -q
python -m evaluation.runner --mode fixture
```

São gerados 30 documentos totalmente sintéticos em layouts e formatos distintos. A avaliação determinística mede consistência do pipeline, **não acurácia real de extração**; métricas de IA permanecem nulas. A avaliação real é opcional, manual e requer autorização/limite explícito de orçamento; os parâmetros representam reservas, não bloqueio de faturamento. O GitHub Actions executa lint, formatação, tipos, testes, avaliação gratuita, build do pacote e build Docker em runners hospedados. Não usa seu computador nem API paga.

## Segurança, limitações e licença

Sem gravação de documentos ou credenciais; entradas são não confiáveis, validação de formato e tamanho e proteção de CSV contra fórmulas. Porém não há autenticação, antimalware, isolamento de parser, limite global de requisições, banco de dados, multipáginas ou prova de origem de cada campo. Não recomendado para produção sem endurecimento adicional. Leia [privacidade](docs/privacy.md). Código da aplicação sob [MIT](LICENSE); dependências possuem licenças próprias.
