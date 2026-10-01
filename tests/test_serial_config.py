import pytest

from tr_serial_proxy.serial_config import parity_value, stopbits_value


@pytest.mark.parametrize("value", list("NEOMS"))
def test_parity_accepts_lowercase(value):
    assert parity_value(value.lower()) == value


@pytest.mark.parametrize("value", ["1", "1.5", "2"])
def test_stopbits_conversion(value):
    assert stopbits_value(value) == float(value)
