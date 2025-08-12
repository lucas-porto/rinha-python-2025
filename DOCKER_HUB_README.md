# 🐳 Deploy para Docker Hub

Este guia explica como fazer o build e push das imagens da aplicação Rinha Python para o Docker Hub.

## 📋 Pré-requisitos

1. **Docker instalado e rodando**
2. **Conta no Docker Hub** (usuário: `lucasportos`)
3. **Login no Docker Hub** executado

## 🔐 Login no Docker Hub

```bash
docker login
```

Digite seu usuário e senha quando solicitado.

## 🚀 Build e Push Automático

### Windows (PowerShell)

```powershell
# Versão padrão (latest)
.\build-and-push.ps1

# Versão específica
.\build-and-push.ps1 v1.0.0
.\build-and-push.ps1 v2.1.3
```

### Linux/Mac (Bash)

```bash
chmod +x build-and-push.sh

# Versão padrão (latest)
./build-and-push.sh

# Versão específica
./build-and-push.sh v1.0.0
./build-and-push.sh v2.1.3
```

## 🔨 Build Manual

Se preferir fazer o processo manualmente:

### 1. Build das Imagens

```bash
# Build com versão específica + latest
docker build -t lucasportos/rinha-python-app:v1.0.0 -t lucasportos/rinha-python-app:latest .
docker build -t lucasportos/rinha-python-worker:v1.0.0 -t lucasportos/rinha-python-worker:latest .

# Build apenas latest
docker build -t lucasportos/rinha-python-app:latest .
docker build -t lucasportos/rinha-python-worker:latest .
```

### 2. Push para Docker Hub

```bash
# Push versão específica
docker push lucasportos/rinha-python-app:v1.0.0
docker push lucasportos/rinha-python-worker:v1.0.0

# Push latest (sempre)
docker push lucasportos/rinha-python-app:latest
docker push lucasportos/rinha-python-worker:latest
```

## 📦 Imagens Disponíveis

Após o push, as seguintes imagens estarão disponíveis:

- **Aplicação**: `lucasportos/rinha-python-app:latest` e `lucasportos/rinha-python-app:v1.0.0`
- **Worker**: `lucasportos/rinha-python-worker:latest` e `lucasportos/rinha-python-worker:v1.0.0`

## 🔗 URLs das Imagens

- **Aplicação**: https://hub.docker.com/r/lucasportos/rinha-python-app
- **Worker**: https://hub.docker.com/r/lucasportos/rinha-python-worker

## 📥 Como Usar as Imagens

### Pull das Imagens

```bash
# Versão específica
docker pull lucasportos/rinha-python-app:v1.0.0
docker pull lucasportos/rinha-python-worker:v1.0.0

# Última versão
docker pull lucasportos/rinha-python-app:latest
docker pull lucasportos/rinha-python-worker:latest
```

### Executar com Docker Compose

```yaml
services:
  app:
    image: lucasportos/rinha-python-app:latest
    # ou versão específica: image: lucasportos/rinha-python-app:v1.0.0
    # ... outras configurações
  
  worker:
    image: lucasportos/rinha-python-worker:latest
    # ou versão específica: image: lucasportos/rinha-python-worker:v1.0.0
    # ... outras configurações
```

## 🏷️ Versionamento

### Estratégia de Versionamento

- **latest**: Sempre aponta para a versão mais recente
- **v1.0.0**: Versões específicas (semantic versioning)
- **v1.1.0**: Versões com melhorias
- **v2.0.0**: Versões com breaking changes

### Exemplos de Uso

```bash
# Desenvolvimento - sempre usa latest
docker pull lucasportos/rinha-python-app:latest

# Produção - usa versão específica
docker pull lucasportos/rinha-python-app:v1.2.0

# Testes - usa versão específica
docker pull lucasportos/rinha-python-app:v1.1.5
```

## 🔍 Verificação

Para verificar se as imagens foram enviadas com sucesso:

```bash
# Listar imagens locais
docker images | grep lucasportos

# Verificar no Docker Hub
docker search lucasportos/rinha-python

# Verificar tags disponíveis
docker manifest inspect lucasportos/rinha-python-app:latest
```

## 🚨 Troubleshooting

### Erro de Autenticação
```bash
docker login
```

### Erro de Permissão
```bash
# Windows: Executar PowerShell como Administrador
# Linux/Mac: Usar sudo se necessário
```

### Erro de Rede
- Verificar conexão com a internet
- Verificar se o Docker Hub está acessível

### Erro de Versão
- Certifique-se de que a versão não contém caracteres especiais
- Use apenas números, pontos e hífens: `v1.0.0`, `v2.1.3`

## 📝 Notas

- As imagens são construídas a partir do Dockerfile na raiz do projeto
- O processo de build pode demorar alguns minutos na primeira execução
- Certifique-se de que o Dockerfile está atualizado antes do build
- A tag `latest` é sempre atualizada, mesmo quando você especifica uma versão
- Use versionamento semântico para suas releases: `vMAJOR.MINOR.PATCH`
