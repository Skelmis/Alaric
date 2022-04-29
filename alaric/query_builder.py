from alaric import AQ
from alaric.comparison import IN
from alaric.comparison.comparison_eq import EQ
from alaric.logical import OR, AND

if __name__ == "__main__":
    eq_1 = EQ("field_1", 15)
    eq_2 = EQ("field_2", 15)
    logical_or = OR(eq_1, eq_2)
    eq_3 = EQ("field_3", True)
    in_1 = IN("field_4", [1, 5, 7, 82, 7])
    logical_or_2 = OR(eq_3, in_1)

    logical_and = AND(logical_or, logical_or_2)
    print(AQ(logical_and).build())
