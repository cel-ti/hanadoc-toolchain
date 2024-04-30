
from functools import update_wrapper
import click
import os
import toml 
import hanadoc_toolchain

def clickCatch(fn):
    def wrapper(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except Exception as e:
            click.echo(f"an error occured:({str(type(e))}) {e}", err=True)
        
    return update_wrapper(wrapper, fn)

def identify(key):
    key1 = key
    key1cfg = toml.load(os.path.join(hanadoc_toolchain.entries[key1], 'hanadoc.config'))

    if "link" not in key1cfg:
        click.echo(f"{key1} is not linked")
        return None, None

    key2 = key1cfg['link']
    key2type = toml.load(os.path.join(hanadoc_toolchain.entries[key2], 'hanadoc.config'))['type']

    if key2type == 'static':
        statickey = key2
        postkey = key1
    else:
        statickey = key1
        postkey = key2

    click.echo(f"static: {statickey}, post: {postkey}")
    assert isinstance(postkey, str)
    assert isinstance(statickey, str)
    return statickey, postkey

next_link = """
<a href="https://hanadoc.vercel.app/{basename}/{filename}" class="btn btn-primary">Next</a>
"""

pre_link = """
<a href="https://hanadoc.vercel.app/{basename}/{filename}" class="btn btn-primary">Previous</a>
"""