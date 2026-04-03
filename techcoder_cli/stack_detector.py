import os

# Maps a marker file/dir to (stack_name, extra_prompt_lines)
_MARKERS = [
    ('pubspec.yaml',       'Flutter/Dart',  "You are an expert in Flutter and Dart. Follow Flutter best practices, use proper widget composition, and suggest null-safe Dart code."),
    ('package.json',       'Node.js/JS',    "You are an expert in Node.js, JavaScript, and TypeScript. Check package.json to understand the exact framework (React, Next.js, Vue, Express, etc.) and follow its conventions."),
    ('requirements.txt',   'Python',        "You are an expert in Python. Follow PEP 8, suggest type hints, and use idiomatic Python patterns."),
    ('pyproject.toml',     'Python',        "You are an expert in Python. Follow PEP 8, suggest type hints, and use idiomatic Python patterns."),
    ('Cargo.toml',         'Rust',          "You are an expert in Rust. Follow ownership/borrowing best practices and use idiomatic Rust patterns."),
    ('go.mod',             'Go',            "You are an expert in Go. Follow standard Go project layout and idiomatic Go patterns."),
    ('pom.xml',            'Java/Maven',    "You are an expert in Java and Maven. Follow Java best practices and Spring conventions where applicable."),
    ('build.gradle',       'Kotlin/Gradle', "You are an expert in Kotlin/Java with Gradle. Follow Android or JVM best practices."),
    ('composer.json',      'PHP',           "You are an expert in PHP. Follow PSR standards and modern PHP patterns."),
    ('Gemfile',            'Ruby',          "You are an expert in Ruby and Ruby on Rails. Follow Ruby idioms and Rails conventions."),
]


def detect_stack(path: str = '.') -> tuple[str, str]:
    """
    Scan `path` for known marker files.
    Returns (stack_name, extra_prompt) — both empty strings if nothing detected.
    """
    for marker, stack, prompt in _MARKERS:
        if os.path.exists(os.path.join(path, marker)):
            return stack, prompt

    # Fallback: check file extensions in top-level directory
    try:
        files = os.listdir(path)
    except OSError:
        return '', ''

    extensions = {os.path.splitext(f)[1] for f in files}
    if '.dart' in extensions:
        return 'Flutter/Dart', _MARKERS[0][2]
    if '.ts' in extensions or '.tsx' in extensions:
        return 'TypeScript', "You are an expert in TypeScript. Use strict typing and modern TS patterns."
    if '.py' in extensions:
        return 'Python', _MARKERS[2][2]

    return '', ''
