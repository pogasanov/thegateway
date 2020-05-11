import json

from prestashop.runner import importer

importer.list_of_categories()

mapping_dict = dict()

for category_id, category_name in importer.categories.items():
    mapping_dict[category_id] = dict(
        src_name=category_name,
        categories=[
            dict(
                PL='',
                EN='',
            ),
        ],
    )

f = open(f'NEW_{importer.category_mapping_filename}.py', 'w', encoding='utf8')
f.write('category_mappings = ')
dumped = json.dumps(mapping_dict, indent=4, sort_keys=True, ensure_ascii=False).replace('}\n', '},\n').replace('"\n', '",\n')
f.write(dumped)
