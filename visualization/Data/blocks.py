


class CFBlock:
    block_start = -1
    block_end = -1
    file_name = ""
    line_start = -1
    line_end = -1
    function_name = ""
    code = ""

    def __init__(self, block_start, block_end, file_name, line_start, line_end, function_name, code_raw):
        self.block_start = block_start
        self.block_end = block_end
        self.file_name = file_name
        self.line_start = line_start
        self.line_end = line_end
        self.function_name = function_name
        self.code = code_raw

    def show(self):
        print(f"[BLOCK] ({hex(self.block_start)} -> {hex(self.block_end)})\n  {self.file_name}::{self.line_start} -> {self.line_end} ({self.function_name})\n--------\n{self.code}\n--------")

    def print_range(self):
        print(f"[BLOCK] ({hex(self.block_start)} -> {hex(self.block_end)})\n")