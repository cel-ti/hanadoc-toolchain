
import os
import typing
import toml 

mod_folder = os.path.dirname(os.path.realpath(__file__))
hanadoc_config = os.path.join(mod_folder, "hanadoc.config")

if not os.path.exists(os.path.join(mod_folder, "hanadoc.config")):
    with open(os.path.join(mod_folder, "hanadoc.config"), "w") as f:
        pass

    entries = {}
else:
    with open(os.path.join(mod_folder, "hanadoc.config"), "r") as f:
        entries = toml.load(f)

entries : typing.Dict[str, str] 

def save():
    with open(os.path.join(mod_folder, "hanadoc.config"), "w") as f:
        toml.dump(entries, f)

