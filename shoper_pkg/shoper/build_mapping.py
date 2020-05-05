import json
from urllib.parse import urlparse

from shoper.runner import (
    importer,
    SHOPER_BASE_URL,
)

categories = importer.get_categories_list()

mapping_dict = dict()

for category_id, category_name in categories.items():
    mapping_dict[category_id] = dict(
        src_name=category_name,
        categories=[
            dict(
                PL='',
                EN='',
            ),
        ],
    )

mapping_filename = f'category_mappings_{urlparse(SHOPER_BASE_URL).netloc}.py'
f = open(f'NEW_{mapping_filename}', 'w', encoding='utf8')
f.write('category_mappings = ')
dumped = json.dumps(mapping_dict, indent=4, sort_keys=True, ensure_ascii=False).replace('}\n', '},\n').replace('"\n', '",\n')
f.write(dumped)
