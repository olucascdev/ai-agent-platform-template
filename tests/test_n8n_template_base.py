"""Contratos do workflow base n8n da fase 9.1."""

from pathlib import Path
import json


def _load_n8n_template() -> dict:
    workflow_path = Path(__file__).resolve().parents[1] / "n8n" / "workflows" / "whatsapp-template-base.json"
    return json.loads(workflow_path.read_text(encoding="utf-8"))


def test_n8n_template_has_required_top_level_structure() -> None:
    """Workflow deve ter estrutura importavel minima do n8n."""
    template = _load_n8n_template()

    assert template["name"]
    assert isinstance(template["nodes"], list)
    assert isinstance(template["connections"], dict)
    assert template["active"] is False


def test_n8n_template_uses_env_var_for_api_url_and_timeout() -> None:
    """URL/timeout do HTTP node devem ser configurados por env vars."""
    template = _load_n8n_template()
    http_node = next(node for node in template["nodes"] if node["name"] == "Forward To API")

    parameters = http_node["parameters"]
    assert parameters["url"] == "={{ $env.API_PLATFORM_BASE_URL + '/webhook/whatsapp' }}"
    assert parameters["options"]["timeout"] == "={{ Number($env.API_PLATFORM_TIMEOUT_MS || 20000) }}"


def test_n8n_template_uses_http_header_credential_binding() -> None:
    """Node de envio deve usar credencial n8n em vez de token hardcoded."""
    template = _load_n8n_template()
    http_node = next(node for node in template["nodes"] if node["name"] == "Forward To API")

    assert http_node["parameters"]["authentication"] == "genericCredentialType"
    assert http_node["parameters"]["genericAuthType"] == "httpHeaderAuth"
    assert http_node["credentials"]["httpHeaderAuth"]["name"] == "AI Platform Header Auth"


def test_n8n_template_has_no_hardcoded_bearer_token_literal() -> None:
    """Template nao deve carregar segredo/token literal no JSON."""
    workflow_path = Path(__file__).resolve().parents[1] / "n8n" / "workflows" / "whatsapp-template-base.json"
    raw = workflow_path.read_text(encoding="utf-8")

    assert "Bearer " not in raw
    assert "sk-" not in raw
