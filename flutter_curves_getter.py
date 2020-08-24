from lxml import html
import re
import requests

URL = "https://api.flutter.dev/flutter/animation/Curves-class.html"

page = requests.get(url = URL)
tree = html.fromstring(page.content)

constants = tree.xpath('//dt[contains(@class, "constant")]/span[contains(@class, "name")]/a/text()')

definitions = []
mappings = []

declaration = 'static const'
var_prefix = 'curves_key_'
key_suffix = '_curve\';\n'
class_prefix = 'Curves.'
class_sufix = ',\n'
pattern = re.compile(r'(?<!^)(?=[A-Z])')
for constant in constants:
    snake_case_constant = pattern.sub('_', constant).lower()
    variable = f'{var_prefix}{snake_case_constant}'

    definition = f'{declaration} {variable} = \'{snake_case_constant}{key_suffix}'
    definitions.append(definition)

    var_map = f'{variable}: {class_prefix}{constant}{class_sufix}'
    mappings.append(var_map)


curves_import = 'import \'package:flutter/animation.dart\';'
class_name = 'CurvesValues'
result_file = open(f'{pattern.sub("_", class_name).lower()}.dart', 'w')

result_file.write(f'{curves_import}\n\n')
result_file.write(f'class {class_name} ' + '{\n')

for definition in definitions:
    result_file.write(f'\t{definition}')

map_def = '\tstatic const translation = {\n'
result_file.write(f'\n{map_def}')

for var_map in mappings:
    result_file.write(f'\t\t{var_map}')

result_file.write('\t};\n}')
result_file.close()