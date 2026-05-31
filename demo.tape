# Generate demo.gif with: vhs demo.tape
# Install vhs: https://github.com/charmbracelet/vhs

Output demo.gif

Set Shell "bash"
Set FontSize 16
Set Width 120
Set Height 36
Set Theme "Dracula"
Set Padding 10

# Install and list
Type "pip install -e . -q" Sleep 500ms Enter
Sleep 2s

Type "llm-bench --help" Enter
Sleep 2s

Type "llm-bench list" Enter
Sleep 3s

# Run benchmark (fake key shows CLI in action; API error is expected without a real key)
Type "OPENAI_API_KEY=sk-demo llm-bench run --model gpt-4o --skills coding" Enter
Sleep 4s

# Serve startup (Ctrl+C after 2s)
Type "llm-bench serve --port 8080" Enter
Sleep 3s
Ctrl+C
Sleep 500ms
