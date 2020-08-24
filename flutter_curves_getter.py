from lxml import html
import re
import requests

URL = "https://api.flutter.dev/flutter/animation/Curves-class.html"

page = requests.get(url = URL)
tree = html.fromstring(page.content)

constants = tree.xpath('//dt[contains(@class, "constant")]/span[contains(@class, "name")]/a/text()')

prefix = 'static const curves_key_'
suffix = '_curve\';'

pattern = re.compile(r'(?<!^)(?=[A-Z])')
for constant in constants:
    snake_case_constant = pattern.sub('_', constant).lower()
    print(f'{prefix}{snake_case_constant} = \'{snake_case_constant}{suffix}')