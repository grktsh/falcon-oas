from setuptools import setup

setup(
    use_scm_version={
        'write_to': 'falcon_oas/__version__.py',
        'write_to_template': '__version__ = {version!r}\n',
    }
)
