from setuptools import setup

setup(
    # https://github.com/pypa/setuptools/issues/1136
    package_dir={'': 'src'},
    use_scm_version={
        'write_to': 'src/falcon_oas/__version__.py',
        'write_to_template': '__version__ = {version!r}\n',
    },
)
