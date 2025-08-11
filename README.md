# Rinha de Backend 2025 - Python

Backend para processamento de pagamentos desenvolvido para a Rinha de Backend 2025.

## Descrição

Sistema de processamento de pagamentos com arquitetura distribuída, utilizando workers assíncronos para processar pagamentos através de múltiplos processadores de pagamento.

## Arquitetura

- **API REST**: Starlette/FastAPI para endpoints HTTP
- **Workers**: Processamento assíncrono com múltiplos workers
- **Redis**: Fila de mensagens e armazenamento de dados
- **HAProxy**: Load balancer para distribuição de carga
- **Docker**: Containerização completa da aplicação

## Endpoints

### POST /payments
Recebe requisições de pagamentos para processamento.

**Payload:**
```json
{
    "correlationId": "uuid-válido",
    "amount": 100.50
}
```

**Resposta:** HTTP 201 (Created)

### GET /payments-summary
Retorna resumo dos pagamentos processados.

**Parâmetros opcionais:**
- `from`: Timestamp ISO para início do período
- `to`: Timestamp ISO para fim do período

**Resposta:**
```json
{
    "default": {
        "totalRequests": 1000,
        "totalAmount": 19900.0,
        "totalFee": 995.0,
        "feePerTransaction": 0.05
    },
    "fallback": {
        "totalRequests": 50,
        "totalAmount": 995.0,
        "totalFee": 149.25,
        "feePerTransaction": 0.15
    }
}
```

## Configuração

### Variáveis de Ambiente

- `REDIS_URL`: URL do Redis (padrão: redis://redis:6379)
- `PROCESSOR_DEFAULT_URL`: URL do processador default
- `PROCESSOR_FALLBACK_URL`: URL do processador fallback

### Configurações do Worker

- `NUM_WORKERS`: 3 workers simultâneos
- `MAX_CONCURRENT_REQUESTS`: 10 requisições concorrentes por worker
- `MAX_RETRIES`: 3 tentativas antes de desistir
- `REDIS_TIMEOUT`: 0.2s timeout para operações Redis

## Melhorias Implementadas

### Processador de Pagamentos

- **Endpoint correto**: Implementado endpoint `/payments` conforme especificação
- **Payload completo**: Envio de `correlationId`, `amount` e `requestedAt`
- **UUID válido**: Validação e geração de UUIDs válidos
- **Timeouts otimizados**: Configuração adequada de timeouts HTTP

### Worker de Processamento

- **Lógica de fallback**: Processamento sequencial default -> fallback -> error
- **Tratamento de erros**: Captura e tratamento adequado de exceções
- **Salvamento consistente**: Dados salvos com processador correto
- **Processamento paralelo**: Múltiplos workers funcionando simultaneamente

### Armazenamento

- **Redis otimizado**: Uso do Redis para fila e dados
- **Estrutura de dados**: Pagamentos organizados por timestamp
- **Separação por processador**: Dados filtrados por tipo de processador
- **Consistência**: Garantia de consistência entre worker e API

### Performance

- **Timeouts HTTP**: 3.0s total, 0.5s connect, 2.0s read
- **Timeouts processador**: 2.5s padrão
- **Pool de conexões**: Reutilização de conexões HTTP
- **Processamento assíncrono**: Operações não-bloqueantes

## Execução

### Desenvolvimento Local

```bash
# Instalar dependências
uv pip install -e .
```

### Testes

```bash
# Executar testes k6
cd rinha-test
k6 run rinha.js
```

## Monitoramento

### Verificar Fila de Pagamentos
```bash
docker exec rinha-redis redis-cli llen payment_queue
```

### Verificar Pagamentos Processados
```bash
docker exec rinha-redis redis-cli zcard payments_by_date
```

### Verificar Resumo
```bash
curl http://localhost:9999/payments-summary
```

## Estrutura do Projeto

```
app/
├── client/          # Cliente HTTP para processadores
├── database/        # Configuração Redis e storage
├── processor/       # Lógica de processamento
├── routes/          # Endpoints da API
├── worker/          # Workers de processamento
└── main.py          # Aplicação principal
```

## Tecnologias

- **Python 3.11**: Linguagem principal
- **Starlette**: Framework web assíncrono
- **Redis**: Banco de dados e fila de mensagens
- **Docker**: Containerização
- **HAProxy**: Load balancer

## Licença

Este projeto foi desenvolvido para a Rinha de Backend 2025.