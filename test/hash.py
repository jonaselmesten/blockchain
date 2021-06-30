from util.hash_util import file_to_hash


def print_file_hash(file_a, file_b):
    assert file_to_hash(file_a) is not file_to_hash(file_b)

hash = file_to_hash("../file.pdf")
print(hash)
