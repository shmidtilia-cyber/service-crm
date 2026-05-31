from pathlib import Path
import re

# 1) Делаем акт читаемым и равномерным по листу
p = Path('templates/crm/print/acceptance_act.html')
s = p.read_text(encoding='utf-8')

style = r'''<style>
@page{size:A4;margin:10mm}
*{box-sizing:border-box}
body{font-family:Arial,sans-serif;color:#000;margin:0;font-size:13px;line-height:1.24}
.page{width:190mm;margin:0 auto}
.header{display:grid;grid-template-columns:1fr 180px;gap:18px;margin-bottom:24px}
.company{font-size:17px;line-height:1.18}
.company b{font-size:16px}
.company .phone{font-size:22px;line-height:1.05}
.right{text-align:right;font-size:15px;padding-top:42px;line-height:1.18}
.barcode,.barcode-num{display:none!important}
.title{text-align:center;font-size:15px;text-decoration:underline;margin:0 0 24px;font-weight:700}
.info{display:grid;grid-template-columns:1fr 1fr;gap:34px;margin-bottom:24px;font-size:14px;line-height:1.22}
.info b{font-weight:800}
.terms{font-size:12px;line-height:1.18;text-align:left}
.terms p{margin:0 0 3px 0}
.signs{display:grid;grid-template-columns:1fr 1fr;gap:38px;margin-top:24px;font-size:13px;line-height:1.18}
.sign-right{text-align:right}
@media print{
  .no-print{display:none!important}
  body{margin:0}
}
</style>'''

s = re.sub(r'<style>.*?</style>', style, s, flags=re.S)
s = re.sub(r'\s*<div class="barcode">.*?</div>\s*<div class="barcode-num">.*?</div>', '', s, flags=re.S)
s = re.sub(
    r'<div>Приемщик:.*?</div>\s*<div class="sign-right">',
    '<div>Приемщик: _____________________</div>\n    <div class="sign-right">',
    s,
    flags=re.S
)

# Убираем автопечать со страницы, так как печатать будет скрытый iframe.
s = s.replace('<body onload="setTimeout(()=>window.print(),300)">', '<body>')
s = s.replace("<body onload=\"setTimeout(()=>window.print(),300)\">", '<body>')
p.write_text(s, encoding='utf-8')

# 2) Меняем печать: не открываем новую вкладку, печатаем через скрытый iframe
p = Path('templates/crm/dashboard.html')
s = p.read_text(encoding='utf-8')

iframe_func = r'''
function printUrlInHiddenFrame(url){
  let frame = document.getElementById('hiddenPrintFrame');
  if(frame) frame.remove();
  frame = document.createElement('iframe');
  frame.id = 'hiddenPrintFrame';
  frame.style.position = 'fixed';
  frame.style.right = '0';
  frame.style.bottom = '0';
  frame.style.width = '0';
  frame.style.height = '0';
  frame.style.border = '0';
  frame.style.opacity = '0';
  document.body.appendChild(frame);
  frame.onload = function(){
    setTimeout(function(){
      frame.contentWindow.focus();
      frame.contentWindow.print();
    }, 350);
  };
  frame.src = url;
}
'''

if 'function printUrlInHiddenFrame(url)' not in s:
    marker = '<script id="real-print-docs-menu-v1">'
    if marker in s:
        s = s.replace(marker, marker + '\n' + iframe_func, 1)
    else:
        s = s.replace('</body>', '<script id="hidden-print-frame-helper">\n' + iframe_func + '\n</script>\n</body>')

s = s.replace("window.open('/print/acceptance/' + orderId + '/', '_blank');", "printUrlInHiddenFrame('/print/acceptance/' + orderId + '/');")
s = s.replace('window.open("/print/acceptance/" + orderId + "/", "_blank");', 'printUrlInHiddenFrame("/print/acceptance/" + orderId + "/");')

p.write_text(s, encoding='utf-8')

print('OK: acceptance print is readable and prints via hidden iframe')
