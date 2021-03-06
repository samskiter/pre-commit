from __future__ import absolute_import
from __future__ import unicode_literals

import pytest

import pre_commit.constants as C
from pre_commit.commands.migrate_config import _indent
from pre_commit.commands.migrate_config import migrate_config
from pre_commit.runner import Runner


@pytest.mark.parametrize(
    ('s', 'expected'),
    (
        ('', ''),
        ('a', '    a'),
        ('foo\nbar', '    foo\n    bar'),
        ('foo\n\nbar\n', '    foo\n\n    bar\n'),
        ('\n\n\n', '\n\n\n'),
    ),
)
def test_indent(s, expected):
    assert _indent(s) == expected


def test_migrate_config_normal_format(tmpdir, capsys):
    cfg = tmpdir.join(C.CONFIG_FILE)
    cfg.write(
        '-   repo: local\n'
        '    hooks:\n'
        '    -   id: foo\n'
        '        name: foo\n'
        '        entry: ./bin/foo.sh\n'
        '        language: script\n',
    )
    assert not migrate_config(Runner(tmpdir.strpath, C.CONFIG_FILE))
    out, _ = capsys.readouterr()
    assert out == 'Configuration has been migrated.\n'
    contents = cfg.read()
    assert contents == (
        'repos:\n'
        '-   repo: local\n'
        '    hooks:\n'
        '    -   id: foo\n'
        '        name: foo\n'
        '        entry: ./bin/foo.sh\n'
        '        language: script\n'
    )


def test_migrate_config_document_marker(tmpdir):
    cfg = tmpdir.join(C.CONFIG_FILE)
    cfg.write(
        '# comment\n'
        '\n'
        '---\n'
        '-   repo: local\n'
        '    hooks:\n'
        '    -   id: foo\n'
        '        name: foo\n'
        '        entry: ./bin/foo.sh\n'
        '        language: script\n',
    )
    assert not migrate_config(Runner(tmpdir.strpath, C.CONFIG_FILE))
    contents = cfg.read()
    assert contents == (
        '# comment\n'
        '\n'
        '---\n'
        'repos:\n'
        '-   repo: local\n'
        '    hooks:\n'
        '    -   id: foo\n'
        '        name: foo\n'
        '        entry: ./bin/foo.sh\n'
        '        language: script\n'
    )


def test_migrate_config_list_literal(tmpdir):
    cfg = tmpdir.join(C.CONFIG_FILE)
    cfg.write(
        '[{\n'
        '    repo: local,\n'
        '    hooks: [{\n'
        '        id: foo, name: foo, entry: ./bin/foo.sh,\n'
        '        language: script,\n'
        '    }]\n'
        '}]',
    )
    assert not migrate_config(Runner(tmpdir.strpath, C.CONFIG_FILE))
    contents = cfg.read()
    assert contents == (
        'repos:\n'
        '    [{\n'
        '        repo: local,\n'
        '        hooks: [{\n'
        '            id: foo, name: foo, entry: ./bin/foo.sh,\n'
        '            language: script,\n'
        '        }]\n'
        '    }]'
    )


def test_already_migrated_configuration_noop(tmpdir, capsys):
    contents = (
        'repos:\n'
        '-   repo: local\n'
        '    hooks:\n'
        '    -   id: foo\n'
        '        name: foo\n'
        '        entry: ./bin/foo.sh\n'
        '        language: script\n'
    )
    cfg = tmpdir.join(C.CONFIG_FILE)
    cfg.write(contents)
    assert not migrate_config(Runner(tmpdir.strpath, C.CONFIG_FILE))
    out, _ = capsys.readouterr()
    assert out == 'Configuration is already migrated.\n'
    assert cfg.read() == contents
