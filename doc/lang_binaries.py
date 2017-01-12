import functools
import operator
import subprocess
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst.directives.tables import ListTable

from camisole.languages import all


def build_list(binaries):
    if not binaries:
        return [nodes.Text("")]
    l = nodes.bullet_list()
    for binary in binaries:
        li = nodes.list_item()
        li.append(nodes.literal(text=binary))
        l.append(li)
    return [l]


class PackageFinder:
    name = None
    cmd = []

    def available(self):
        return Path(self.cmd[0]).exists()

    def for_binary(self, binary):
        try:
            return {line.split(b':', 1)[0].decode() for line
                    in
                    subprocess.check_output(self.cmd + [binary]).splitlines()}
        except subprocess.CalledProcessError:
            return set()

    def for_binaries(self, binaries):
        return functools.reduce(
            operator.ior, (self.for_binary(binary) for binary in binaries))


class DebianFinder(PackageFinder):
    name = "Debian"
    cmd = ['/usr/bin/apt-file', 'search', '-lFaam64']


class ArchFinder(PackageFinder):
    name = "Arch"
    cmd = ['/usr/bin/pkgfile', '-qb']


class CamisoleLanguageTable(ListTable):
    has_content = False
    package_finders = [inst for inst in (DebianFinder(), ArchFinder())
                       if inst.available()]

    def run(self):
        self.options['widths'] = 'auto'
        title, messages = self.make_title()

        headers = [[nodes.paragraph(text="Language")],
                   [nodes.paragraph(text="Class")],
                   [nodes.paragraph(text="Binaries")]]

        for f in self.package_finders:
            headers.append([nodes.paragraph(text=f"{f.name} packages")])

        table_body = []
        for cls in sorted(all().values(), key=lambda e: e.name.lower()):
            binaries = set(cls.required_binaries())
            if not binaries:
                continue
            body = [[nodes.paragraph(text=cls.name)],
                    [nodes.literal(text=cls.__name__)],
                    build_list(binaries)]
            for f in self.package_finders:
                body.append(build_list(f.for_binaries(binaries)))
            table_body.append(body)

        table = [headers] + table_body
        self.check_table_dimensions(table, 1, 0)
        widths, col_widths = self.get_column_widths(len(headers))
        table_node = self.build_table_from_list(table, widths, col_widths, 1, 0)
        if title:
            table_node.insert(0, title)
        return [table_node] + messages


def setup(app):
    app.add_directive('camisole-language-table', CamisoleLanguageTable)
    return {'version': '0.1'}
