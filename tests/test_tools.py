import pytest


def test_calculator_is_exact_and_rejects_code_and_unbounded_work():
    from ada.tools import calculate

    assert calculate("(0.1 + 0.2) * 10") == "3"
    assert calculate("1 / 3") == "1/3"
    assert calculate("-2 * (3 + 4)") == "-14"
    for expression in (
        "__import__('os')",
        "open('secret')",
        "2 ** 999999",
        "1/0",
        "True+1",
        "1e1000",
        "(" * 20 + "1" + ")" * 20,
        "+".join(["1"] * 100),
        "999999999999 * 999999999999",
        "1; print(2)",
    ):
        with pytest.raises(ValueError):
            calculate(expression)
