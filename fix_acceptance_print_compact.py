from pathlib import Path

p = Path('templates/crm/print/acceptance_act.html')
s = p.read_text(encoding='utf-8')

# Убираем штрихкод и номер штрихкода
s = s.replace('<div class="barcode">||||||||||||||||</div>\n      <div class="barcode-num">{{ barcode }}</div>', '')
s = s.replace('<div class="barcode">||||||||||||||||</div>\r\n      <div class="barcode-num">{{ barcode }}</div>', '')

# Делаем документ компактнее, чтобы помещался в 1 лист A4
s = s.replace('@page{size:A4;margin:10mm}', '@page{size:A4;margin:8mm}')
s = s.replace('body{font-family:Arial,sans-serif;color:#000;margin:0;font-size:13px;line-height:1.22}', 'body{font-family:Arial,sans-serif;color:#000;margin:0;font-size:11px;line-height:1.12}')
s = s.replace('.page{width:190mm;margin:0 auto}', '.page{width:194mm;margin:0 auto}')
s = s.replace('.header{display:grid;grid-template-columns:1fr 220px;gap:20px;margin-bottom:38px}', '.header{display:grid;grid-template-columns:1fr 190px;gap:18px;margin-bottom:18px}')
s = s.replace('.company{font-size:20px}', '.company{font-size:15px;line-height:1.12}')
s = s.replace('.company b{font-size:15px}', '.company b{font-size:14px}')
s = s.replace('.company .phone{font-size:24px}', '.company .phone{font-size:20px}')
s = s.replace('.right{text-align:right;font-size:16px;padding-top:48px}', '.right{text-align:right;font-size:14px;padding-top:38px}')
s = s.replace('.barcode{font-family:"Arial Black",Arial,sans-serif;letter-spacing:2px;font-size:28px;line-height:20px;margin-top:18px}\n.barcode-num{font-size:17px}', '')
s = s.replace('.title{text-align:center;font-size:15px;text-decoration:underline;margin:0 0 24px}', '.title{text-align:center;font-size:13px;text-decoration:underline;margin:0 0 18px}')
s = s.replace('.info{display:grid;grid-template-columns:1fr 1fr;gap:40px;margin-bottom:28px;font-size:15px}', '.info{display:grid;grid-template-columns:1fr 1fr;gap:34px;margin-bottom:16px;font-size:13px}')
s = s.replace('.terms{font-size:13px;text-align:left}', '.terms{font-size:10.2px;line-height:1.08;text-align:left}')
s = s.replace('.signs{display:grid;grid-template-columns:1fr 1fr;gap:40px;margin-top:28px;font-size:15px}', '.signs{display:grid;grid-template-columns:1fr 1fr;gap:40px;margin-top:18px;font-size:12px}')

# Подписи аккуратнее: без длинного ФИО, чтобы не разрывало строку
old = '''<div>Приемщик: _____________________ {% if order.manager %}{{ order.manager.first_name|default:order.manager.username }}{% endif %}</div>
    <div class="sign-right">_____________________ Клиент<br>с условиями ремонта ознакомлен и согласен</div>'''
new = '''<div>Приемщик: _____________________</div>
    <div class="sign-right">_____________________ Клиент<br>с условиями ремонта ознакомлен и согласен</div>'''
s = s.replace(old, new)

# Страховка: если старый CSS штрихкода остался отдельной строкой
s = s.replace('.barcode-num{font-size:17px}', '')

p.write_text(s, encoding='utf-8')
print('OK: acceptance act compacted, barcode removed')
