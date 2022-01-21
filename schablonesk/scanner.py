import re


class Scanner:

    def __init__(self):
        self.cmd_line_begin = re.compile("\\s*:>(.+)")

    def _scan_lines(self, lines):
        blocks = []
        command_block = None
        text_block = None

        for line in lines:
            match = self.cmd_line_begin.match(line)
            if match:
                if text_block is not None:
                    blocks.append(text_block)
                    text_block = None
                if command_block is None:
                    command_block = _CommandBlock()
                command_block.add(match.group(1))
            else:
                if command_block is not None:
                    blocks.append(command_block)
                    command_block = None
                if text_block is None:
                    text_block = _TextBlock()
                text_block.add_text_line(line)

        if command_block is not None:
            blocks.append(command_block)
        if text_block is not None:
            blocks.append(text_block)

        return blocks


class _CommandBlock:

    def __init__(self):
        self.command = ""

    def add(self, line):
        self.command += line


class _TextBlock:

    def __init__(self):
        self.lines = []

    def add_text_line(self, line):
        self.lines.append(line)
