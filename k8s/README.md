# Manifests de Kubernetes (exemplo)

Estes manifests são um **exemplo ilustrativo** de como a aplicação poderia
ser implantada em um cluster Kubernetes — não são necessários para rodar o
projeto localmente (para isso, veja o `docker-compose.yml` na raiz).

## Arquivos

- `backend-configmap.yaml` — configuração (ConfigMap) e um Secret de exemplo para o backend.
- `backend-deployment.yaml` — Deployment + Service do backend (FastAPI).
- `frontend-deployment.yaml` — Deployment + Service do frontend (Nginx servindo os estáticos do React).

## Como aplicar (exemplo)

```bash
kubectl create namespace event-management
kubectl -n event-management apply -f backend-configmap.yaml
kubectl -n event-management apply -f backend-deployment.yaml
kubectl -n event-management apply -f frontend-deployment.yaml
```

## Observações importantes

- **Imagens**: os manifests referenciam `event-management-backend:latest` e
  `event-management-frontend:latest`. Em um pipeline real, essas tags viriam
  de um registry (ex: `ghcr.io/sua-org/event-management-backend:sha-abc123`),
  publicadas pela pipeline de CI/CD.
- **Persistência**: o backend usa SQLite por padrão neste desafio, montado em
  um `emptyDir` (efêmero) só para o Deployment subir sem erro. Para produção
  real, o caminho recomendado é trocar `DATABASE_URL` para Postgres (ex: um
  banco gerenciado ou o operador `CloudNativePG`) e então escalar
  `replicas` do backend com segurança.
- **Secrets**: o `Secret` no `backend-configmap.yaml` é apenas ilustrativo.
  Em produção, secrets não devem ir para o Git — use `kubectl create secret`,
  um External Secrets Operator, Sealed Secrets ou um vault gerenciado.
- **Ingress**: não incluímos um `Ingress` porque isso depende do controller
  disponível no cluster (nginx-ingress, Traefik, etc.) e do domínio real. Em
  produção, um `Ingress` exporia o `event-management-frontend` publicamente
  e faria proxy de `/api` para o `event-management-backend`, evitando expor
  a API diretamente.
