from pathlib import Path

p = Path('templates/crm/dashboard.html')
s = p.read_text(encoding='utf-8')

# CSS: compact popup like RemOnline reference
replacements = {
    ".status-menu{display:none;position:absolute;top:30px;left:0;width:260px;background:#fff;border:1px solid #d9dee3;border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,.16);z-index:50;padding:10px}":
    ".status-menu{display:none;position:absolute;top:30px;left:0;width:520px;background:#fff;border:1px solid #d9dee3;border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,.16);z-index:9999;padding:12px}",
    ".status-menu{display:none;position:absolute;top:30px;left:0;min-width:920px;max-width:1200px;background:#fff;border:1px solid #d9dee3;border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,.16);z-index:9999;padding:12px}":
    ".status-menu{display:none;position:absolute;top:30px;left:0;width:520px;background:#fff;border:1px solid #d9dee3;border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,.16);z-index:9999;padding:12px}",
    ".status-group{color:#6b7280;font-size:13px;margin:8px 0 5px}":
    ".status-group{color:#6b7280;font-size:13px;font-weight:700;margin:10px 0 6px}.status-row{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 10px 0}",
    ".status-group{display:block;clear:both;color:#6b7280;font-size:13px;font-weight:700;margin:10px 0 6px}":
    ".status-group{color:#6b7280;font-size:13px;font-weight:700;margin:10px 0 6px}.status-row{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 10px 0}",
    ".status-group{color:#6b7280;font-size:13px;font-weight:700;margin:10px 0 6px}.status-menu form{display:block}.status-menu .status-item{display:inline-block}":
    ".status-group{color:#6b7280;font-size:13px;font-weight:700;margin:10px 0 6px}.status-row{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 10px 0}",
    ".status-item{border:0;color:#fff;border-radius:4px;padding:5px 8px;margin:2px 4px 4px 0;font-weight:700;cursor:pointer}":
    ".status-item{border:0;color:#fff;border-radius:4px;padding:5px 8px;margin:0;font-weight:700;cursor:pointer;white-space:nowrap;display:inline-block}",
    ".status-item{border:0;color:#fff;border-radius:4px;padding:5px 8px;margin:2px 4px 6px 0;font-weight:700;cursor:pointer;white-space:nowrap}":
    ".status-item{border:0;color:#fff;border-radius:4px;padding:5px 8px;margin:0;font-weight:700;cursor:pointer;white-space:nowrap;display:inline-block}",
}
for a, b in replacements.items():
    s = s.replace(a, b)

# Ensure status td is not clipping popup
s = s.replace(
    ".orders-table td{padding:8px 10px;border-bottom:1px solid #edf1f4;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}",
    ".orders-table td{padding:8px 10px;border-bottom:1px solid #edf1f4;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.orders-table td[data-col='status']{overflow:visible}"
)

# HTML: wrap every group buttons in .status-row. There are two status menus: table and order card.
old = "{% for group,statuses in status_groups.items %}<div class=\"status-group\">{{ group }}</div>{% for key,label in statuses %}<button class=\"status-item st-{{ key }}\" name=\"status\" value=\"{{ key }}\" type=\"submit\">{{ label }}</button>{% endfor %}{% endfor %}"
new = "{% for group,statuses in status_groups.items %}<div class=\"status-group\">{{ group }}</div><div class=\"status-row\">{% for key,label in statuses %}<button class=\"status-item st-{{ key }}\" name=\"status\" value=\"{{ key }}\" type=\"submit\">{{ label }}</button>{% endfor %}</div>{% endfor %}"
s = s.replace(old, new)

# If previous patch left duplicate status-row wrappers, normalize simple duplicates.
s = s.replace('<div class="status-row"><div class="status-row">', '<div class="status-row">')
s = s.replace('</div></div>{% endfor %}', '</div>{% endfor %}')

p.write_text(s, encoding='utf-8')
print('OK: status menu layout fixed')
