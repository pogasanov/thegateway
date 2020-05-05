import json
from urllib.parse import urlparse

from prestashop.runner import (
    importer,
    prestashop_base_url,
)

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

mapping_filename = f'category_mappings_{urlparse(prestashop_base_url).netloc}.py'
f = open(f'NEW_{mapping_filename}', 'w', encoding='utf8')
f.write('category_mappings = ')
dumped = json.dumps(mapping_dict, indent=4, sort_keys=True, ensure_ascii=False).replace('}\n', '},\n').replace('"\n', '",\n')
f.write(dumped)
