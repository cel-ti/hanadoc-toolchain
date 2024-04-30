from hanadoc_toolchain.__main__ import hanadoc
import click
import hanadoc_toolchain.utils

@hanadoc.group("z_internal", help="internal helper commands")
def internal():
    pass

@internal.command("identify")
@click.argument("key", type=click.STRING)
@hanadoc_toolchain.utils.clickCatch
def identify(key):
    return hanadoc_toolchain.utils.identify(key)