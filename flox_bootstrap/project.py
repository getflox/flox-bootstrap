import os
import re
import shutil
from os.path import isdir
from pathlib import Path
from shutil import copy2

import stringcase
from floxcore import CONFIG_DIRS
from floxcore.console import warning, error_box
from floxcore.context import Flox
from floxcore.remotes import universal_copy, generate_cache_hash
from jinja2 import Environment, FileSystemLoader


def _reload_cache(flox: Flox, cache_dir: str):
    if isdir(cache_dir):
        shutil.rmtree(cache_dir)

    for repository in flox.settings.bootstrap.repositories:
        universal_copy(flox, cache_dir, repository)


def enable(flox: Flox, features: tuple, no_cache: bool, **kwargs):
    """Bootstraps project with given templates"""
    cache_dir = CONFIG_DIRS.get_in("user", "templates-cache")

    if not len(flox.settings.bootstrap.repositories):
        error_box("Repositories not configured. Run: flox configure --plugin=bootstrap")
        return

    if no_cache or not isdir(cache_dir):
        _reload_cache(flox, cache_dir)

    existing_paths = []
    for template_name in features:
        for repository in flox.settings.bootstrap.repositories:
            template_path = os.path.join(cache_dir, generate_cache_hash(repository), template_name)
            if os.path.isdir(template_path):
                existing_paths.append(template_path)

    non_existing = set(features) - set([Path(p).parts[-1] for p in existing_paths])
    for name in non_existing:
        warning(f'Bootstrap "{name}" does not exist')

    variables = {
        "project_name": flox.name,
        "project_name_hyphen": stringcase.spinalcase(flox.name),
        "project_name_underscore": stringcase.snakecase(flox.name),
        "project_name_camel_case": stringcase.pascalcase(flox.name),
    }

    for template_path in existing_paths:
        env = Environment(loader=FileSystemLoader(template_path))

        for item in Path(template_path).glob("**/*"):
            relative_path = str(item).replace(template_path, "").strip("/")

            item_destination = os.path.join(flox.working_dir, relative_path)
            item_destination = re.sub(r"(<(.*?)>)", "{\\2}", item_destination).format(**variables)

            if os.path.isdir(str(item)):
                os.makedirs(item_destination, exist_ok=True)
            else:
                if not item_destination.endswith(".j2"):
                    copy2(str(item), item_destination)
                else:
                    template = env.get_template(relative_path)
                    template.stream(**variables).dump(item_destination.replace(".j2", ""))
