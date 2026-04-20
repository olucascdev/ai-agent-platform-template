"""
Testes para validar documentacao de onboarding.
"""

from pathlib import Path


def test_onboarding_doc_exists():
    """Valida que o guia de onboarding existe."""
    doc_path = Path("docs/ONBOARDING.md")
    assert doc_path.exists(), "ONBOARDING.md deve existir"
    assert doc_path.is_file(), "ONBOARDING.md deve ser um arquivo"


def test_configuration_doc_exists():
    """Valida que a documentacao de configuracao existe."""
    doc_path = Path("docs/CONFIGURATION.md")
    assert doc_path.exists(), "CONFIGURATION.md deve existir"
    assert doc_path.is_file(), "CONFIGURATION.md deve ser um arquivo"


def test_customization_doc_exists():
    """Valida que o guia de customizacao existe."""
    doc_path = Path("docs/CUSTOMIZATION.md")
    assert doc_path.exists(), "CUSTOMIZATION.md deve existir"
    assert doc_path.is_file(), "CUSTOMIZATION.md deve ser um arquivo"


def test_examples_directory_exists():
    """Valida que o diretorio de exemplos existe."""
    examples_dir = Path("docs/examples")
    assert examples_dir.exists(), "Diretorio docs/examples/ deve existir"
    assert examples_dir.is_dir(), "docs/examples/ deve ser um diretorio"


def test_example_configs_exist():
    """Valida que os exemplos de configuracao existem."""
    examples = [
        "helena-openai.env.example",
        "helena-openrouter.env.example",
        "helena-groq.env.example",
        "custom-crm.env.example",
        "production.env.example",
    ]
    
    for example in examples:
        example_path = Path(f"docs/examples/{example}")
        assert example_path.exists(), f"Exemplo {example} deve existir"


def test_examples_readme_exists():
    """Valida que o README de exemplos existe."""
    readme_path = Path("docs/examples/README.md")
    assert readme_path.exists(), "docs/examples/README.md deve existir"


def test_onboarding_has_required_sections():
    """Valida que o onboarding tem todas as secoes obrigatorias."""
    doc_path = Path("docs/ONBOARDING.md")
    content = doc_path.read_text()
    
    required_sections = [
        "Pre-requisitos",
        "Passo 1: Clone do repositorio",
        "Passo 2: Configuracao de variaveis de ambiente",
        "Passo 3: Inicializacao do banco de dados",
        "Passo 4: Primeira conversa de teste",
        "Troubleshooting",
    ]
    
    for section in required_sections:
        assert section in content, f"Secao '{section}' deve estar no onboarding"


def test_configuration_has_all_variable_categories():
    """Valida que a configuracao documenta todas as categorias de variaveis."""
    doc_path = Path("docs/CONFIGURATION.md")
    content = doc_path.read_text()
    
    categories = [
        "Banco de Dados",
        "Provider de Modelo de IA",
        "CRM",
        "WhatsApp Sender",
        "Preprocessor Multimodal",
        "Agente",
        "Observabilidade",
    ]
    
    for category in categories:
        assert category in content, f"Categoria '{category}' deve estar documentada"


def test_configuration_documents_required_variables():
    """Valida que variaveis obrigatorias estao documentadas."""
    doc_path = Path("docs/CONFIGURATION.md")
    content = doc_path.read_text()
    
    required_vars = [
        "DATABASE_URL",
        "DATABASE_URL_MIGRATIONS",
        "AGENT_MODEL_PROVIDER",
        "AGENT_MODEL_ID",
        "AGENT_MODEL_API_KEY",
        "CRM_BASE_URL",
        "CRM_API_TOKEN",
        "WHATSAPP_SENDER_BASE_URL",
        "WHATSAPP_SENDER_API_TOKEN",
    ]
    
    for var in required_vars:
        assert var in content, f"Variavel '{var}' deve estar documentada"


def test_customization_has_all_guides():
    """Valida que o guia de customizacao cobre todos os topicos."""
    doc_path = Path("docs/CUSTOMIZATION.md")
    content = doc_path.read_text()
    
    topics = [
        "Prompts e Regras de Conversa",
        "Departamentos e Transferencias",
        "FAQ e Qualificacao",
        "Guardrails e Limites",
        "Integracoes (CRM e Sender)",
        "Preprocessor Multimodal",
        "Provider de Modelo",
    ]
    
    for topic in topics:
        assert topic in content, f"Topico '{topic}' deve estar no guia"


def test_example_configs_have_required_variables():
    """Valida que exemplos de configuracao tem variaveis obrigatorias."""
    required_vars = [
        "DATABASE_URL",
        "AGENT_MODEL_PROVIDER",
        "CRM_BASE_URL",
        "WHATSAPP_SENDER_BASE_URL",
    ]
    
    examples = [
        "helena-openai.env.example",
        "helena-openrouter.env.example",
        "custom-crm.env.example",
    ]
    
    for example in examples:
        example_path = Path(f"docs/examples/{example}")
        content = example_path.read_text()
        
        for var in required_vars:
            assert var in content, f"Exemplo {example} deve ter variavel {var}"


def test_feature_10_2_documentation_exists():
    """Valida que a documentacao da feature 10.2 existe."""
    feature_path = Path("docs/features/fase-10-f10.2.md")
    assert feature_path.exists(), "Documentacao da feature 10.2 deve existir"
