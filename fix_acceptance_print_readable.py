from pathlib import Path
import re

p = Path('templates/crm/print/acceptance_act.html')
s = p.read_text(encoding='utf-8')

# Убираем старые CSS-правки и задаем один нормальный читаемый стиль.
s = re.sub(r'<style>.*?</style>', r'''<style>
@page{size:A4;margin:8mm}
*{box-sizing:border-box}
body{font-family:Arial,sans-serif;color:#000;margin:0;font-size:12px;line-height:1.16}
.page{width:194mm;margin:0 auto}
.header{display:grid;grid-template-columns:1fr 170px;gap:16px;margin-bottom:18px}
.company{font-size:15px;line-height:1.12}
.company b{font-size:14px}
.company .phone{font-size:20px;line-height:1.05}
.right{text-align:right;font-size:14px;padding-top:36px;line-height:1.15}
.barcode,.barcode-num{display:none!important}
.title{text-align:center;font-size:13px;text-decoration:underline;margin:0 0 18px}
.info{display:grid;grid-template-columns:1fr 1fr;gap:30px;margin-bottom:16px;font-size:13px;line-height:1.16}
.info b{font-weight:800}
.terms{font-size:11px;line-height:1.11;text-align:left}
.signs{display:grid;grid-template-columns:1fr 1fr;gap:38px;margin-top:18px;font-size:12px;line-height:1.15}
.sign-right{text-align:right}
@media print{
  .no-print{display:none!important}
  body{margin:0}
}
</style>''', s, flags=re.S)

# Если штрихкод остался в HTML — удаляем.
s = re.sub(r'\s*<div class="barcode">.*?</div>\s*<div class="barcode-num">.*?</div>', '', s, flags=re.S)

# Убираем перенос ФИО приемщика, оставляем чистую подпись.
s = re.sub(
    r'<div>Приемщик:.*?</div>\s*<div class="sign-right">',
    '<div>Приемщик: _____________________</div>\n    <div class="sign-right">',
    s,
    flags=re.S
)

p.write_text(s, encoding='utf-8')
print('OK: readable A4 acceptance act style applied')
