MODEL = 'gemma4:e4b'

BASE_SYSTEM_PROMPT = """You are TechCoder CLI, an expert coding assistant.
You help developers write, debug, and improve code.

Your rules:
- Always provide clean, working code
- Explain your code clearly
- Suggest best practices
- If asked something unrelated to coding, politely redirect to coding topics
"""


def build_system_prompt(stack_prompt: str = '') -> str:
    """Combine base prompt with optional stack-specific expertise."""
    if stack_prompt:
        return BASE_SYSTEM_PROMPT.rstrip() + f"\n\nStack-specific guidance:\n{stack_prompt}\n"
    return BASE_SYSTEM_PROMPT
