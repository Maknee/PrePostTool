""" Usage: call with <filename> <typename>
"""

import clang.cindex

import sys
import json
import re
import argparse

libclang_lib = '/usr/lib/x86_64-linux-gnu/libclang-6.0.so.1'
clang.cindex.Config.set_library_file(libclang_lib)

class Parser:
    def __init__(self):
        pass

    def ParseFunction(self, line):
        pass

class RegexMatchingData:
    def __init__(self, function_name, pre_operation = "", post_operation = ""):
        self.function_name = function_name
        self.pre_operation = pre_operation
        self.post_operation = post_operation

class ToWrite:
    def __init__(self, pre, line, column, data):
        self.pre = pre
        self.line = line
        self.column = column
        self.data = data

class ToWriteContainer:
    def __init__(self, filename):
        self.headers = []
        self.matching_datas = []

        with open(filename, 'r') as f:
            json_data = json.load(f)
            for header in json_data["headers"]:
                self.headers.append(header["include"])
            for matching_data in json_data["matching_datas"]:
                m_data = RegexMatchingData(matching_data["function_name"], matching_data["pre_operation"], matching_data["post_operation"])
                self.matching_datas.append(m_data)

class CParser(Parser):
    def __init__(self, filename, to_write_c):
        Parser.__init__(self)
        
        self.filename =  filename
        index = clang.cindex.Index.create()
        self.cursor = index.parse(filename).cursor

        self.headers = to_write_c.headers
        self.matching_datas = to_write_c.matching_datas
        self.to_writes = []

        with open(filename, "r") as f:
            self.lines = f.readlines()

    def Run(self, node):
        if node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
            for matching_data in self.matching_datas:
                re_match = re.compile(matching_data.function_name)
                if re_match.match(node.spelling):
                    start = node.extent.start.line - 1
                    end = node.extent.end.line - 1

                    #find {
                    while not '{' in self.lines[start]:
                        start = start + 1

                    start_column = self.lines[start].find('{')
                    
                    #find }
                    while not '}' in self.lines[end]:
                        end = end - 1

                    end_column = self.lines[end].find('}')

                    to_write_start = ToWrite(True, start, start_column, matching_data.pre_operation)
                    to_write_end = ToWrite(False, end, end_column, matching_data.post_operation)

                    self.to_writes.append(to_write_start)
                    self.to_writes.append(to_write_end)

        for c in node.get_children():
            self.Run(c)

    def Dump(self):
        str = ""
        for header in self.headers:
            str += header + '\n'

        offset_line = 0
        for to_write in self.to_writes:
            line_num = to_write.line + offset_line
            pre = to_write.pre
            column = to_write.column
            data = to_write.data

            if pre:
                # insert data on next line
                self.lines.insert(line_num + 1, data + '\n')
            else:
                # remember everything after and including '{'
                remainder = self.lines[line_num][column:]

                # erase '{'
                self.lines[line_num] = self.lines[line_num][:column]

                self.lines.insert(line_num + 1, '\n' + data + '\n' + remainder)

            offset_line = offset_line + 1
        
        for line in self.lines:
            str += line

        with open(self.filename, "w") as f:
            f.write(str)

parser = argparse.ArgumentParser(description = 'PrePostTool')
parser.add_argument('files', nargs = '+')
parser.add_argument('json_data', help='json file containing matching data')

args = parser.parse_args()

to_write_c = ToWriteContainer(args.json_data)

a = CParser('test.c', to_write_c)
a.Run(a.cursor)
a.Dump()