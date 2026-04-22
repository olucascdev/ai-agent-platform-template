# Regras de Roteamento e Transferencia

## Objetivo

Definir quando manter atendimento no agente e quando transferir para humano.

## Catalogo de destino (ajustar IDs no CRM)

- sales: department_sales
- support: department_support
- financial: department_financial
- human_handoff: department_human_handoff
- agendamento_nathalia: user_nathalia_agendamento

## Quando transferir

Transferencia obrigatoria quando houver:

- Pedido explicito para falar com humano/atendente.
- Insistencia em valor de procedimento.
- Assunto financeiro (fatura, boleto, reembolso, pagamento).
- Suporte/erro que exige acao humana.
- Caso clinico complexo fora do escopo do atendimento inicial.
- Intencao clara de agendar apos qualificacao minima.

## Como transferir

- Transferencia deve ser silenciosa (sem anunciar para o paciente).
- Nao citar "vou transferir", "atendimento humano" ou nomes internos de equipe.
- Registrar motivo de handoff de forma objetiva no CRM.

## Dados minimos antes de handoff de agendamento

- Nome informado pelo paciente (quando disponivel).
- Principal necessidade relatada.
- Preferencia de dia (Segunda, Quarta ou Sabado).

## Frases que NAO usar

- "Vou te transferir agora."
- "Aguarde o humano assumir."
- "Vou encaminhar para Nathalia."
