import os
import shutil
import sys
import click
import toml

from hanadoc_toolchain import entries, save, hanadoc_config
import datetime
import hanadoc_toolchain
import hanadoc_toolchain.utils

@click.group()
def hanadoc():
    pass

@hanadoc.command()
@click.argument("type", type=click.Choice(["static", "post"]))
@click.argument("key", type=click.STRING)
def init(type, key):
    """
    if hanadoc.config does not exist, create it.
    if .ignore exists and hanadoc.config does not exist, add entry
    """
    if key in entries:
        click.echo(f"key {key} already exists")
        return
    
    entries[key] = os.path.abspath(os.getcwd())
    save()

    if not os.path.exists('hanadoc.config'):
        with open('hanadoc.config', 'w') as f:
            f.write(f'type="{type}"\n')
            f.write(f'key="{key}"\n')

    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as f:
            f.write('hanadoc.config\n')
    else:
        with open('.gitignore', 'r') as f:
            ignorelines = f.readlines()
        
        if 'hanadoc.config' not in ignorelines:
            with open('.gitignore', 'a') as f:
                f.write('hanadoc.config\n')

    click.echo("Initialized hanadoc config")

@hanadoc.command()
@click.argument("key", type=click.STRING)
def link(key : str):
    if key not in entries:
        click.echo(f"key {key} does not exist")
        return
    
    cfg = toml.load('hanadoc.config')
    cfgtype = cfg['type']
    cfgkey = cfg['key']

    try:
        targetcfg = toml.load(entries[key] + '/hanadoc.config')
    except FileNotFoundError:
        click.echo(f"target {key} does not exist")
        return
    
    if "link" in targetcfg:
        click.echo(f"Already linked {key} to {targetcfg['link']}")
        return
    
    targettype = targetcfg['type']

    if targettype ==cfgtype:
        click.echo(f"Same type for {key} and {cfgkey}")
        return
    
    cfg["link"] = key
    with open('hanadoc.config', 'w') as f:
        toml.dump(cfg, f)

    targetcfg["link"] = cfgkey
    with open(entries[key] + '/hanadoc.config', 'w') as f:
        toml.dump(targetcfg, f)

    click.echo(f"Linked {key} to {cfgkey}")

@hanadoc.command()
@click.option("--list", "-l", is_flag=True)
@click.option("--open", "-o", is_flag=True)
def config(list, open):
    if list:
        for key in entries:
            click.echo(key)
    elif open:
        os.startfile(hanadoc_config)

@hanadoc.group()
def gen(): 
    pass

@gen.command()
@click.pass_context
@click.argument("key", type=click.STRING)
def mhtml1(ctx : click.Context, key):
    skey, pkey = hanadoc_toolchain.utils.identify(key)
    if pkey is None:
        click.echo(f"key {key} does not exist")
        return

    # confirm all files within directory are html
    for fn in os.listdir(os.getcwd()):
        fn :str
        if not fn.endswith('.html'):
            click.echo(f"{fn} is not html")
            return

    # make sure the files had the same prefixes
    # sort 
    basename = None
    
    sorted_list =sorted(os.listdir(os.getcwd()), key=lambda x: os.path.splitext(x)[0])
    
    for fn in sorted_list: 
        fn :str
        if basename is None:
            basename = os.path.splitext(fn)[0]
            continue
        if fn.startswith(basename):
            pass
        else:
            click.echo(f"{fn} does not start with {basename}")
            return

    del fn
    assert basename

    with open(sorted_list[0], 'r+') as f:
        data = f.read()
        lines = [
            "---",
            f"title: '{basename}'",
            # to xxxx-xx-xx
            f"date: '{datetime.datetime.now().strftime('%Y-%m-%d')}'",
            "draft: true",
            "tags:",
            "---",
        ]
        data = '\n'.join(lines) + '\n' + data

        f.seek(0)
        f.write(data)
        f.truncate()

    # work on them
    for i, ff in enumerate(sorted_list):
        click.echo(f"working on {ff}")
        with open(ff, 'a+') as f:
            previousFF = sorted_list[i-1] if i-1 >= 0 else None
            if previousFF:
                f.write(hanadoc_toolchain.utils.pre_link.format(basename=basename, filename=previousFF))
            
            nextFF = sorted_list[i+1] if i+1 < len(sorted_list) else None
            if nextFF:
                f.write(hanadoc_toolchain.utils.next_link.format(basename=basename, filename=nextFF))

        # move file to target
        if i == 0:
            post_path = entries[pkey]
            shutil.copy(ff, os.path.join(post_path, ff))
        else:
            staticpath = entries[skey] # type: ignore
            os.makedirs(os.path.join(staticpath, basename), exist_ok=True)
            shutil.copy(ff, os.path.join(staticpath, basename,ff))

    
from hanadoc_toolchain.internalCmds import internal # noqa
hanadoc.add_command(internal)

if __name__ == "__main__":
    hanadoc()
            


