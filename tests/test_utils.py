from tr_serial_proxy.utils import hex_dump, port_key


def test_hex_dump_preserves_all_byte_values():
    payload = bytes(range(256))
    assert bytes.fromhex(hex_dump(payload)) == payload
    assert hex_dump(b"\x00\xab\xff") == "00 AB FF"
    assert hex_dump(b"") == ""


def test_port_aliases_normalize_for_duplicate_detection():
    assert port_key(" com006 ") == port_key("\\\\.\\COM6") == "COM6"
    assert port_key("COM21") != port_key("COM6")
