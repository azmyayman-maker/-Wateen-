import os

def count_lines():
    loc = 0
    for root, dirs, files in os.walk('.'):
        # Ignore common large directories
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '.venv', '__pycache__', 'venv', 'env', 'dist', 'build']]
        for file in files:
            # Common source code extensions
            if file.endswith(('.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        loc += sum(1 for _ in f)
                except Exception:
                    pass
    return loc

print("Total LOC in project source files (*.py, *.js, *.ts, *.html, *.css):", count_lines())
