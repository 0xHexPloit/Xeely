import base64


def decode_data_containing_base64_content(data: str) -> str:
    items = data.split(" ")
    output = []

    for item in items:
        try:
            decoded_data = base64.b64decode(item).decode("utf-8")
            output.append(str(decoded_data))
        except Exception:
            output.append(item)

    return " ".join(output)
