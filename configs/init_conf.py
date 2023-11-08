DRUG_COLUMN_MAPPER = {('drug',): 'drug',
                      ('product_name',): 'product_name',
                      ('Торгівельна назва', 'trade_name',): 'trade_name',
                      ('Діючі речовини', 'active_ingredients',): 'active_ingredients',
                      ('simply_release_form',): 'simply_release_form',
                      ('Форма випуску', 'release_form',): 'release_form',
                      ('Склад', 'composition',): 'composition',
                      ('Дітям', 'children',): 'children',
                      ('url',): 'url'}

REGULATION_COLUMN_MAPPER = {('#', 'order', 'Order'): 'order',
                            ('Симптом', 'symptom', 'Symptom'): 'symptom'}

# Необходимые имена колонок в Excel file.
REQUIRED_COLUMN_NAMES = list(DRUG_COLUMN_MAPPER.values()) + list(REGULATION_COLUMN_MAPPER.values())

# Имена колонок с контентом о применении препарата - возрастные и весовые ограничения, дозировка, срок применения и др.
CONTENT_COLUMN = ('Спосіб застосування та дози', 'Застосування', )
