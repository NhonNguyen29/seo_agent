"""config_loader.py
Utility to load environment variables from .env file safely.
"""

import os
from pathlib import Path
from typing import Optional


def load_config(env_path: Optional[str] = None) -> dict:
    """
    Load configuration from .env file.
    Falls back to environment variables if .env doesn't exist.
    
    Args:
        env_path: Path to .env file. Defaults to .env in project root.
    
    Returns:
        Dictionary of configuration values.
    """
    if env_path is None:
        env_path = Path(__file__).parent / ".env"
    else:
        env_path = Path(env_path)

    config = {}
    
    # Try to load from .env file
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip().strip("'\"")
    
    # Merge with environment variables (env vars take precedence)
    config.update({k: v for k, v in os.environ.items() 
                   if k in ['SERPER_API_KEY', 'FIRECRAWL_API_KEY', 'OPENROUTER_API_KEY',
                            'LOG_LEVEL', 'OUTPUT_DIR', 'LOG_DIR', 'RESEARCH_RESULTS_PER_KW',
                            'SCRAPER_MAX_PER_KEYWORD', 'SCRAPER_TIMEOUT', 'SCRAPER_DELAY',
                            'SEMANTIC_SIMILARITY_THRESHOLD', 'OUTLINE_MODEL', 'OUTLINE_MAX_TOKENS',
                            'DOMAIN_KEYWORD_MODEL', 'DOMAIN_KEYWORD_MAX_TOKENS',
                            'DOMAIN_KEYWORD_SUGGESTION_LIMIT', 'DOMAIN_FETCH_TIMEOUT',
                            'NLP_MODEL']})
    
    return config


def get_config_value(key: str, default: str = None, env_path: Optional[str] = None) -> str:
    """
    Get a single config value.
    
    Args:
        key: Configuration key name.
        default: Default value if key not found.
        env_path: Path to .env file.
    
    Returns:
        Configuration value or default.
    """
    config = load_config(env_path)
    return config.get(key, default)


def validate_api_keys(config: dict) -> dict:
    """
    Check if API keys are configured (not default placeholders).
    
    Args:
        config: Configuration dictionary.
    
    Returns:
        Dictionary with keys and their validation status.
    """
    keys = {
        'SERPER_API_KEY': 'Serper.dev',
        'FIRECRAWL_API_KEY': 'Firecrawl',
        'OPENROUTER_API_KEY': 'OpenRouter'
    }
    
    status = {}
    for key, name in keys.items():
        value = config.get(key, 'YOUR_' + key)
        is_valid = value and 'YOUR_' not in value
        status[name] = {
            'configured': is_valid,
            'key': key
        }
    
    return status


if __name__ == "__main__":
    # Demo: Load and display config
    cfg = load_config()
    print("Loaded configuration:")
    for k, v in cfg.items():
        # Hide actual API keys for security
        if 'KEY' in k and len(v) > 10:
            print(f"  {k}: {v[:10]}...***")
        else:
            print(f"  {k}: {v}")
    
    print("\nAPI Key validation:")
    validation = validate_api_keys(cfg)
    for name, status in validation.items():
        status_str = "✓ Configured" if status['configured'] else "✗ Missing/Invalid"
        print(f"  {name}: {status_str}")
