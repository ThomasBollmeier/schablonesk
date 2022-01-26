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
        self.patterns = [
            (re.compile("^[a-z_][a-z0-9_]*"), Token.IDENTIFIER)
        ]
        self.whitespace = re.compile("^\\s+")

    def add(self, line):
        self.command += line

    def tokenize(self):
        tokens = []
        remaining = self.command
        while remaining:
            token, remaining = self.match_next(remaining)
            if token is not None:
                tokens.append(token)
        return tokens

    def match_next(self, s):
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
            return Token(max_token_catg, remaining[:max_size]), remaining[max_size:]
        else:
            return Token(Token.UNKNOWN, remaining), ""


class _TextBlock:

    def __init__(self):
        self.text = ""

    def add_text_line(self, line):
        self.text += line + os.linesep

    def tokenize(self):
        return [Token(Token.TEXT, self.text)]
