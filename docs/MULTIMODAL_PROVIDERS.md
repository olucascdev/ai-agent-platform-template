# Guia de Providers Multimodais

Este documento descreve os providers disponíveis para processamento multimodal (áudio, imagem, PDF) no template Agno.

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Transcrição de Áudio](#transcrição-de-áudio)
3. [Análise de Imagem](#análise-de-imagem)
4. [Processamento de PDF](#processamento-de-pdf)
5. [Comparação de Providers](#comparação-de-providers)
6. [Exemplos de Configuração](#exemplos-de-configuração)

---

## Visão Geral

O template suporta múltiplos providers para processamento multimodal, permitindo escolher o melhor custo-benefício para cada caso de uso.

### Providers Disponíveis

| Funcionalidade | Providers Suportados |
|----------------|---------------------|
| **Transcrição de Áudio** | OpenAI, Groq |
| **Análise de Imagem** | Google (Gemini), Groq |
| **Processamento de PDF** | PyPDF (local) |

---

## Transcrição de Áudio

### OpenAI Whisper (Recomendado)

**Modelo**: `whisper-1`

**Configuração**:
```env
AUDIO_TRANSCRIPTION_PROVIDER=openai
AUDIO_TRANSCRIPTION_MODEL=whisper-1
AUDIO_TRANSCRIPTION_LANGUAGE=pt
OPENAI_API_KEY=sk-...
```

**Vantagens**:
- ✅ Melhor qualidade de transcrição
- ✅ Suporta 99+ idiomas
- ✅ Detecta idioma automaticamente
- ✅ Lida bem com sotaques e ruído
- ✅ API estável e confiável

**Desvantagens**:
- ❌ Custo: $0.006 por minuto
- ❌ Limite de arquivo: 25 MB

**Quando usar**:
- Produção com alto volume
- Qualidade é prioridade
- Áudios com ruído ou sotaque forte
- Múltiplos idiomas

---

### Groq Whisper (Alternativa Rápida)

**Modelos disponíveis**:
- `whisper-large-v3` (recomendado)
- `whisper-large-v3-turbo` (mais rápido)
- `distil-whisper-large-v3-en` (apenas inglês)

**Configuração**:
```env
AUDIO_TRANSCRIPTION_PROVIDER=groq
AUDIO_TRANSCRIPTION_MODEL=whisper-large-v3
AUDIO_TRANSCRIPTION_LANGUAGE=pt
GROQ_API_KEY=gsk_...
```

**Vantagens**:
- ✅ Muito rápido (hardware especializado)
- ✅ Gratuito para uso moderado
- ✅ Mesma API do OpenAI
- ✅ Boa qualidade

**Desvantagens**:
- ❌ Rate limits mais restritivos
- ❌ Menos idiomas suportados
- ❌ Qualidade ligeiramente inferior ao OpenAI

**Quando usar**:
- Desenvolvimento e testes
- Baixo volume de transcrições
- Velocidade é prioridade
- Custo é fator crítico

---

## Análise de Imagem

### Google Gemini (Recomendado)

**Modelos disponíveis**:
- `models/gemini-2.0-flash-lite` (padrão, rápido)
- `models/gemini-2.0-flash` (melhor qualidade)
- `models/gemini-1.5-pro` (máxima qualidade)

**Configuração**:
```env
IMAGE_ANALYSIS_PROVIDER=google
IMAGE_ANALYSIS_MODEL=models/gemini-2.0-flash-lite
IMAGE_ANALYSIS_PROMPT=Descreva a imagem e extraia o texto visivel de forma organizada.
GOOGLE_API_KEY=sua-chave-google
```

**Vantagens**:
- ✅ Excelente qualidade de análise
- ✅ OCR muito preciso
- ✅ Entende contexto complexo
- ✅ Gratuito até 1500 requisições/dia
- ✅ Suporta múltiplas imagens

**Desvantagens**:
- ❌ Requer biblioteca `google-generativeai`
- ❌ API diferente do padrão OpenAI

**Quando usar**:
- Análise detalhada de imagens
- OCR de documentos
- Imagens complexas (gráficos, diagramas)
- Produção com volume moderado

---

### Groq Vision (Alternativa)

**Modelos disponíveis**:
- `llama-3.2-90b-vision-preview` (recomendado)
- `llama-3.2-11b-vision-preview` (mais rápido)

**Configuração**:
```env
IMAGE_ANALYSIS_PROVIDER=groq
IMAGE_ANALYSIS_MODEL=llama-3.2-90b-vision-preview
IMAGE_ANALYSIS_PROMPT=Descreva a imagem e extraia o texto visivel de forma organizada.
GROQ_API_KEY=gsk_...
```

**Vantagens**:
- ✅ Muito rápido
- ✅ Gratuito para uso moderado
- ✅ API compatível com OpenAI
- ✅ Boa qualidade geral

**Desvantagens**:
- ❌ OCR inferior ao Gemini
- ❌ Menos detalhes em análises complexas
- ❌ Rate limits mais restritivos

**Quando usar**:
- Desenvolvimento e testes
- Análises simples (identificar objetos, pessoas)
- Velocidade é prioridade
- Custo é fator crítico

---

## Processamento de PDF

### PyPDF (Único Provider)

**Configuração**:
```env
PDF_PROCESSING_PROVIDER=pypdf
PDF_PROCESSING_MAX_PAGES=20
PDF_DOWNLOAD_TIMEOUT_SECONDS=20
```

**Vantagens**:
- ✅ Processamento local (sem custo)
- ✅ Rápido
- ✅ Sem limites de uso
- ✅ Privacidade (não envia para APIs externas)

**Desvantagens**:
- ❌ Apenas extrai texto (não analisa imagens no PDF)
- ❌ Não funciona com PDFs escaneados
- ❌ Não faz OCR

**Quando usar**:
- PDFs com texto selecionável
- Documentos simples
- Quando privacidade é importante

---

## Comparação de Providers

### Transcrição de Áudio

| Critério | OpenAI Whisper | Groq Whisper |
|----------|----------------|--------------|
| **Qualidade** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Velocidade** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Custo** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Idiomas** | 99+ | 50+ |
| **Rate Limit** | Alto | Médio |
| **Recomendado para** | Produção | Dev/Teste |

### Análise de Imagem

| Critério | Google Gemini | Groq Vision |
|----------|---------------|-------------|
| **Qualidade** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **OCR** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Velocidade** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Custo** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Rate Limit** | Alto | Médio |
| **Recomendado para** | Produção | Dev/Teste |

---

## Exemplos de Configuração

### Configuração Híbrida (Recomendada para Produção)

Use o melhor de cada provider:

```env
# Agente: OpenAI (melhor qualidade conversacional)
AGENT_MODEL_PROVIDER=openai
AGENT_MODEL_ID=gpt-4o-mini
OPENAI_API_KEY=sk-...

# Áudio: OpenAI (melhor transcrição)
AUDIO_TRANSCRIPTION_PROVIDER=openai
AUDIO_TRANSCRIPTION_MODEL=whisper-1

# Imagem: Google (melhor OCR e análise)
IMAGE_ANALYSIS_PROVIDER=google
IMAGE_ANALYSIS_MODEL=models/gemini-2.0-flash-lite
GOOGLE_API_KEY=...

# PDF: PyPDF (local, sem custo)
PDF_PROCESSING_PROVIDER=pypdf
```

**Custo estimado**: $10-50/mês (dependendo do volume)

---

### Configuração Groq Total (Desenvolvimento)

Use Groq para tudo:

```env
# Agente: Groq (rápido e gratuito)
AGENT_MODEL_PROVIDER=groq
AGENT_MODEL_ID=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_...

# Áudio: Groq (rápido e gratuito)
AUDIO_TRANSCRIPTION_PROVIDER=groq
AUDIO_TRANSCRIPTION_MODEL=whisper-large-v3

# Imagem: Groq (rápido e gratuito)
IMAGE_ANALYSIS_PROVIDER=groq
IMAGE_ANALYSIS_MODEL=llama-3.2-90b-vision-preview

# PDF: PyPDF (local)
PDF_PROCESSING_PROVIDER=pypdf
```

**Custo estimado**: $0/mês (tier gratuito)

---

### Configuração Custo-Benefício (Produção Pequena)

Balanceie qualidade e custo:

```env
# Agente: Groq (rápido e barato)
AGENT_MODEL_PROVIDER=groq
AGENT_MODEL_ID=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_...

# Áudio: OpenAI (melhor qualidade)
AUDIO_TRANSCRIPTION_PROVIDER=openai
AUDIO_TRANSCRIPTION_MODEL=whisper-1
OPENAI_API_KEY=sk-...

# Imagem: Google (melhor OCR, gratuito)
IMAGE_ANALYSIS_PROVIDER=google
IMAGE_ANALYSIS_MODEL=models/gemini-2.0-flash-lite
GOOGLE_API_KEY=...

# PDF: PyPDF (local)
PDF_PROCESSING_PROVIDER=pypdf
```

**Custo estimado**: $5-20/mês

---

## Troubleshooting

### Erro: "Provider não suportado"

**Causa**: Provider configurado não existe ou está com typo.

**Solução**:
```bash
# Verificar providers válidos
# Áudio: openai, groq
# Imagem: google, groq
# PDF: pypdf

# Verificar configuração
echo $AUDIO_TRANSCRIPTION_PROVIDER
echo $IMAGE_ANALYSIS_PROVIDER
```

---

### Erro: "API Key inválida"

**Causa**: Chave de API não configurada ou inválida.

**Solução**:
```bash
# Verificar se as chaves estão configuradas
echo $OPENAI_API_KEY
echo $GROQ_API_KEY
echo $GOOGLE_API_KEY

# Testar chave isoladamente
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY"
```

---

### Erro: "Rate limit exceeded"

**Causa**: Excedeu limite de requisições do provider.

**Solução**:
1. Aguarde alguns minutos
2. Considere upgrade do plano
3. Ou mude para provider alternativo

---

### Transcrição de áudio falha

**Causa**: Arquivo muito grande ou formato não suportado.

**Solução**:
```bash
# Verificar tamanho do arquivo (máx 25MB)
# Verificar formato (mp3, mp4, wav, webm, m4a)

# Aumentar timeout se necessário
AUDIO_DOWNLOAD_TIMEOUT_SECONDS=30
```

---

### Análise de imagem retorna vazio

**Causa**: Imagem corrompida ou formato não suportado.

**Solução**:
```bash
# Verificar formato (jpg, png, webp, gif)
# Verificar se URL é acessível

# Aumentar timeout se necessário
IMAGE_DOWNLOAD_TIMEOUT_SECONDS=30
```

---

## Referências

- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- [Groq API Documentation](https://console.groq.com/docs)
- [Google Gemini API](https://ai.google.dev/docs)
- [PyPDF Documentation](https://pypdf.readthedocs.io/)

---

**Última atualização**: 23-04-2026
