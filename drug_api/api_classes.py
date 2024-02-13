from dataclasses import dataclass


@dataclass
class Diagnosis:
    excel_file: int # file's id
    name: str
    description: str


@dataclass
class Drugs:
    drug: str # simply drug name from task
    product_name: str
    trade_name: str
    active_ingredients: str
    release_form: str
    simply_release_form: str
    composition: str
    children: str
    url: str
    usage_text: str
    is_processed: bool
    is_disabled: bool


@dataclass
class UsageColumnNames:
    order: int
    column_name: str


@dataclass
class UsageDosage:
    drug: int # drug's id
    usage_column_name: str
    text: str


@dataclass
class Regulations:
    diagnosis: int # diagnosis's id
    drug: int # drug's id
    order: int
    symptom: str
    is_disabled: bool


if __name__ == "__main__":
    from dataclasses import asdict

    usage_column = UsageColumnNames(7, "column")
    print(usage_column)
    print(asdict(usage_column))
