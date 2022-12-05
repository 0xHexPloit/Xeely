from xeely.xxe.decoding import decode_data_containing_base64_content


def test_decoding_data_containing_base64_content():
    input = "Test dmFsdWU="
    output = decode_data_containing_base64_content(input)

    assert output == "Test value"
