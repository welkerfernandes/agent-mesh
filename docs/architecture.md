# Decisões arquiteturais

## Orquestração limitada

Um DAG fixo fornece limites verificáveis de custo de chamadas e profundidade. Planos são validados
antes da execução e não podem adicionar ferramentas fora da allowlist. Orçamentos são reservados sob lock.
A execução do critic TypeScript usa argv fixo, sem shell, timeout e JSON de entrada.

## Separação entre modo de dados e inferência

Dados podem ser demo/live independentemente de a inferência ser demo/Ollama. Cada evidência registra
origem, hash e instante da coleta. O modo demo não representa capacidade cognitiva de um modelo.
Os testes de contrato do Ollama usam transporte simulado; não substituem avaliação com modelo real.

## Fronteiras de confiança

Credencial determina tenant. Modelo pode propor plano e relatório, mas não mudar URLs de ferramentas,
adicionar shell ou criar referências inexistentes. Ainda é necessário avaliar prompt injection, inferências
indevidas e suporte semântico em datasets adversariais. O critic verifica estrutura, não autenticidade da fonte.

## Evolução

Persistir eventos antes de cada transição; introduzir estado durável e idempotência por missão;
avaliar ataques em corpus rotulado; instrumentar tokens/latência/custo; adicionar revisão humana e fila.
Só depois introduzir ciclos de replanejamento com limites, políticas e observabilidade próprios.
