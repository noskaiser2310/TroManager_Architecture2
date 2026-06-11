import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass
sys.path.insert(0, '.')
from src.llm.config_loader import load_llm_config

config = load_llm_config()
print('=== Current LLM Config ===')
print(f'Flash model (System 1): {config.flash_model}')
print(f'Pro model   (System 2): {config.pro_model}')
print(f'Embedding model:        {config.embedding_model} (dim={config.embedding_dim})')
print(f'Base URL:               {config.llm.base_url}')
api_key = config.llm.api_key or ""
is_placeholder = (
    not api_key
    or "MISSING" in api_key
    or "paste" in api_key
    or "your-key" in api_key
    or len(api_key) < 20
)
api_key_set = not is_placeholder
print(f'API key set:            {api_key_set} ({"ready" if api_key_set else "placeholder/empty"})')
print()
if not api_key_set:
    print('[!] GEMINI_API_KEY chua duoc set trong .env (hoac van la placeholder)')
    print('    Edit .env va dien key that vao dong GEMINI_API_KEY=')
else:
    print('[OK] GEMINI_API_KEY da duoc set (khong hien thi gia tri)')
