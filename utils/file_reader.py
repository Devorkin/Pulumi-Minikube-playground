def readFileContentInBytes(path: str = None) -> bytes:
    with open(path, "rb") as file:
        loaded_content: bytes = file.read()
    file.close()
    return loaded_content


def readFileContent(path: str = None) -> bytes:
    with open(path, "r") as file:
        loaded_content: bytes = file.read()
    file.close()
    return loaded_content
