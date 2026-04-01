"""
Rich display utilities for Agent Memory Workshop notebooks.
Uses IPython.display.HTML for color-coded, readable output in Jupyter.
"""
from IPython.display import display, HTML

# Color palette
_COLORS = {
    "green": "#22c55e",
    "blue": "#3b82f6",
    "amber": "#f59e0b",
    "red": "#ef4444",
    "purple": "#a855f7",
    "gray": "#9ca3af",
    "white": "#f9fafb",
    "dark": "#1f2937",
}

def _html(content):
    display(HTML(content))

def status(msg):
    """Blue info line."""
    _html(f'<div style="color:{_COLORS["blue"]};font-family:monospace;padding:2px 0">ℹ️ {msg}</div>')

def success(msg):
    """Green success line."""
    _html(f'<div style="color:{_COLORS["green"]};font-family:monospace;padding:2px 0">✅ {msg}</div>')

def error(msg):
    """Red error line."""
    _html(f'<div style="color:{_COLORS["red"]};font-family:monospace;padding:2px 0">❌ {msg}</div>')

def warning(msg):
    """Amber warning line."""
    _html(f'<div style="color:{_COLORS["amber"]};font-family:monospace;padding:2px 0">⚠️ {msg}</div>')

def section(title):
    """Bold section header with divider."""
    _html(
        f'<div style="border-top:2px solid {_COLORS["blue"]};margin:12px 0 6px 0;padding-top:8px">'
        f'<strong style="color:{_COLORS["white"]};font-family:monospace;font-size:14px">{title}</strong>'
        f'</div>'
    )

def subsection(title):
    """Lighter subsection header."""
    _html(
        f'<div style="border-top:1px solid {_COLORS["gray"]};margin:8px 0 4px 0;padding-top:6px">'
        f'<strong style="color:{_COLORS["gray"]};font-family:monospace;font-size:12px">{title}</strong>'
        f'</div>'
    )

def tool_call(name, args):
    """Amber tool call display."""
    args_str = str(args) if len(str(args)) < 200 else str(args)[:200] + "..."
    _html(
        f'<div style="background:#1c1917;border-left:3px solid {_COLORS["amber"]};padding:6px 10px;margin:4px 0;font-family:monospace;border-radius:0 4px 4px 0">'
        f'<span style="color:{_COLORS["amber"]}">🔧 {name}</span>'
        f'<span style="color:{_COLORS["gray"]};margin-left:8px">{args_str}</span>'
        f'</div>'
    )

def tool_result(preview, is_error=False):
    """Tool result display, indented."""
    color = _COLORS["red"] if is_error else _COLORS["amber"]
    icon = "❌" if is_error else "↳"
    preview = str(preview)
    if len(preview) > 300:
        preview = preview[:300] + "..."
    preview = preview.replace("<", "&lt;").replace(">", "&gt;")
    _html(
        f'<div style="color:{color};font-family:monospace;padding:2px 0 2px 24px;font-size:12px">'
        f'{icon} {preview}'
        f'</div>'
    )

def llm_response(text, label="LLM Response"):
    """Purple block for LLM/agent responses."""
    text = str(text)
    text = text.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
    _html(
        f'<div style="background:#1a1025;border-left:3px solid {_COLORS["purple"]};padding:8px 12px;margin:6px 0;border-radius:0 4px 4px 0">'
        f'<div style="color:{_COLORS["purple"]};font-family:monospace;font-size:11px;margin-bottom:4px"><strong>{label}</strong></div>'
        f'<div style="color:{_COLORS["white"]};font-family:monospace;font-size:13px;line-height:1.5">{text}</div>'
        f'</div>'
    )

def context_bar(percent, tokens, max_tokens):
    """Horizontal bar showing context window usage."""
    bar_color = _COLORS["green"] if percent < 50 else _COLORS["amber"] if percent < 80 else _COLORS["red"]
    width = min(percent, 100)
    _html(
        f'<div style="font-family:monospace;margin:4px 0">'
        f'<div style="display:flex;align-items:center;gap:8px">'
        f'<span style="color:{_COLORS["gray"]};font-size:11px;min-width:120px">Context: {tokens:,}/{max_tokens:,}</span>'
        f'<div style="flex:1;background:#374151;border-radius:4px;height:14px;overflow:hidden">'
        f'<div style="width:{width}%;background:{bar_color};height:100%;border-radius:4px;transition:width 0.3s"></div>'
        f'</div>'
        f'<span style="color:{bar_color};font-size:12px;min-width:50px;text-align:right">{percent:.1f}%</span>'
        f'</div></div>'
    )

def iteration(n, max_n):
    """Gray iteration counter."""
    _html(
        f'<div style="color:{_COLORS["gray"]};font-family:monospace;font-size:11px;padding:4px 0;border-bottom:1px dotted {_COLORS["gray"]}">'
        f'⟳ Iteration {n}/{max_n}'
        f'</div>'
    )

def query_header(query, thread_id=None, query_num=None, total=None):
    """Prominent query header."""
    meta = ""
    if query_num and total:
        meta += f"Query {query_num}/{total}"
    if thread_id:
        meta += f" · thread: {thread_id}" if meta else f"thread: {thread_id}"
    _html(
        f'<div style="background:#172554;border:1px solid {_COLORS["blue"]};padding:10px 14px;margin:10px 0 6px 0;border-radius:6px">'
        f'<div style="color:{_COLORS["gray"]};font-family:monospace;font-size:11px;margin-bottom:4px">{meta}</div>'
        f'<div style="color:{_COLORS["white"]};font-family:monospace;font-size:14px"><strong>❓ {query}</strong></div>'
        f'</div>'
    )

def memory_write(memory_type, detail=""):
    """Show a memory write operation."""
    _html(
        f'<div style="color:{_COLORS["green"]};font-family:monospace;font-size:12px;padding:1px 0 1px 16px">'
        f'💾 {memory_type}{" — " + detail if detail else ""}'
        f'</div>'
    )

def memory_read(memory_type, count=None):
    """Show a memory read operation."""
    extra = f" ({count} items)" if count is not None else ""
    _html(
        f'<div style="color:{_COLORS["blue"]};font-family:monospace;font-size:12px;padding:1px 0 1px 16px">'
        f'📖 {memory_type}{extra}'
        f'</div>'
    )

def comparison_header(label, is_engineered=True):
    """Header for memory vs naive comparison sections."""
    color = _COLORS["green"] if is_engineered else _COLORS["red"]
    icon = "🧠" if is_engineered else "📋"
    _html(
        f'<div style="background:{"#052e16" if is_engineered else "#2c0b0e"};border:1px solid {color};padding:8px 12px;margin:10px 0 4px 0;border-radius:6px">'
        f'<strong style="color:{color};font-family:monospace">{icon} {label}</strong>'
        f'</div>'
    )

def timing(seconds):
    """Gray timing info."""
    _html(
        f'<span style="color:{_COLORS["gray"]};font-family:monospace;font-size:11px">⏱ {seconds:.1f}s</span>'
    )

def table(headers, rows):
    """Render a simple HTML table."""
    header_html = "".join(f'<th style="text-align:left;padding:6px 12px;border-bottom:2px solid {_COLORS["blue"]};color:{_COLORS["blue"]};font-family:monospace;font-size:12px">{h}</th>' for h in headers)
    rows_html = ""
    for row in rows:
        cells = "".join(f'<td style="padding:4px 12px;border-bottom:1px solid #374151;color:{_COLORS["white"]};font-family:monospace;font-size:12px">{c}</td>' for c in row)
        rows_html += f"<tr>{cells}</tr>"
    _html(
        f'<table style="border-collapse:collapse;margin:6px 0">'
        f'<thead><tr>{header_html}</tr></thead>'
        f'<tbody>{rows_html}</tbody></table>'
    )
