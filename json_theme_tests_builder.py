import re

class TestGroup:
    def __init__(self, text_block, title_pattern, entry_pattern, entry_def_pattern):
        self.text_block = text_block
        self.title_pattern = title_pattern
        self.entry_pattern = entry_pattern
        self.entry_def_pattern = entry_def_pattern
        self.title = self._get_title()
        self.has_entry = self._has_defined_entry()

    def add_new_test(self):
        new_test_group, was_success = self.text_block, False
        if self.has_entry:
            to_insert = f'\nexpect(ThemeDecoder.decode{self.title}(entry), entry);'
            insert_where = self.entry_def_pattern.search(self.text_block)
            if insert_where != None:
                position = insert_where.span()[1]
                new_test_group = self.text_block[:position+1] + to_insert + self.text_block[position:]
                was_success = True
        else:
            after_check_expression = re.compile(r'null\)\,\s*null\,?\s*\);')
            insert_where = list(after_check_expression.finditer(self.text_block))[-1]
            position = insert_where.span()[1]

            to_insert = self._copy_from_test()
            if to_insert != None:
                obj_expression = re.compile(r'\s*\,\s*[a-zA-Z0-9]+\.[a-zA-Z0-9]+\,?')
                obj = obj_expression.search(to_insert).group(0).replace(',','').strip()
                replaceable_expression = re.compile(r'\s*\(\s*[^\()]+\s*\)\s*\,')
                replaceable_position = replaceable_expression.search(to_insert).span()
                if to_insert[len(to_insert)-3] != ' ':
                    suffix = to_insert[replaceable_position[1]-1:-2] + ',' +  to_insert[len(to_insert)-2:]
                else:
                    suffix = to_insert[replaceable_position[1]-1:]
                to_insert = to_insert[:replaceable_position[0]] + f'({obj},)' + suffix
                new_test_group = self.text_block[:position+1] + f'\n{to_insert}' + self.text_block[position:]
                was_success = True

        return new_test_group, was_success

    def _get_title(self):
        title = self.title_pattern.search(self.text_block).group(0)[6:-1]
        return title

    def _has_defined_entry(self):
        entry = self.entry_pattern.search(self.text_block)
        return entry != None

    def _copy_from_test(self):
        to_search = r'expect\(\s*ThemeDecoder\.decode' + self.title + r'\(\s*.*\s*\),\s+[a-zA-Z0-9]+\.[a-zA-Z]+\,?\s*\)\;' 
        pattern = re.compile(to_search)
        test = pattern.search(self.text_block)
        if test != None:
            test = test.group(0)
        return test
        

origin_path = '../json_theme/test/json_theme_test.dart'
dart_file_name = 'json_theme_test.dart'

f = open(origin_path, 'r')
contents = f.read()
f.close()

pattern = re.compile(r'(test\(\')')
groups = pattern.split(contents)
groups, header = iter(groups[1:]), groups[0]
test_groups = [group + next(groups, '') for group in groups]

new_test = '\t\texpect(ThemeDecoder.'
title_pattern = re.compile(r'test\(\'[a-zA-Z0-9]+\'')
entry_pattern = re.compile(r' entry')
entry_def_pattern = re.compile(r'entry\s*=\s*[\_a-zA-Z0-9]+(\s*[^;]*)+\;')

to_manually_edit = []
f = open(dart_file_name, 'w')
f.write(header)
for i,test_group in enumerate(test_groups):
    group = TestGroup(test_group, title_pattern, entry_pattern, entry_def_pattern)
    new_group, was_success = group.add_new_test()
    f.write(new_group)
    if not was_success:
        to_manually_edit.append(group.title)

f.close()

print('Failed with automatization. Required human intervention')
for title in to_manually_edit:
    print(title)