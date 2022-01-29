import os
import re
from schablonesk.tokens import Token


class Scanner:

    def __init__(self):
        self.cmd_line_begin = re.compile("^\\s*:>(.+)")

    def scan(self, code):
        ret = []
        for block in self._scan_lines(code.split("\n")):
            ret += block.tokenize()
        return ret

    def _scan_lines(self, lines):
        blocks = []
        command_block = None
        text_block = None

        for line_num, line in enumerate(lines):
            line_num += 1  # start line counting from 1
            match = self.cmd_line_begin.match(line)
            if match:
                if text_block is not None:
                    blocks.append(text_block)
                    text_block = None
                if command_block is None:
                    command_block = _CommandBlock()
                command_block.add(line_num, match.group(1))
            else:
                if command_block is not None:
                    blocks.append(command_block)
                    command_block = None
                if text_block is None:
                    text_block = _TextBlock(line_num)
                text_block.add_text_line(line)

        if command_block is not None:
            blocks.append(command_block)
        if text_block is not None:
            blocks.append(text_block)

        return blocks


class _CommandBlock:

    def __init__(self):
        self.lines = []
        self.patterns = [
            (re.compile("\\."), Token.DOT),
            (re.compile("^[a-z_][a-z0-9_]*"), Token.IDENTIFIER)
        ]
        self.whitespace = re.compile("^\\s+")

    def add(self, line_num, commands):
        self.lines.append((line_num, commands))

    def tokenize(self):
        all_tokens = []
        for line_num, commands in self.lines:
            all_tokens += self._tokenize_commands(line_num, commands)
        return all_tokens

    def _tokenize_commands(self, line_num, commands):
        tokens = []
        remaining = commands
        while remaining:
            token, remaining = self.match_next(remaining, line_num)
            if token is not None:
                tokens.append(token)
        return tokens

    def match_next(self, s, line_num):
        remaining = s

        # Skip whitespace
        match_res = self.whitespace.match(remaining)

        if match_res:
            remaining = remaining[match_res.end():]
        if not remaining:
            return None, remaining

        # Find maximal munch:
        max_token_catg = None
        max_size = 0
        for regex, token_catg in self.patterns:
            match_res = regex.match(remaining)
            if match_res:
                size = match_res.end()
                if max_token_catg is None or size > max_size:
                    max_token_catg = token_catg
                    max_size = size
        if max_token_catg:
            return Token(max_token_catg,
                         remaining[:max_size],
                         line_num), remaining[max_size:]
        else:
            return Token(Token.UNKNOWN, remaining, line_num), ""


class _TextBlock:

    def __init__(self, start_line_num):
        self.text = ""
        self.start_line_num = start_line_num

    def add_text_line(self, line):
        self.text += line + os.linesep

    def tokenize(self):
        return [Token(Token.TEXT, self.text, self.start_line_num)]
