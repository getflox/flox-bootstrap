import importlib
import os
import re
import shutil
from collections import OrderedDict
from os.path import isdir, isfile, join, abspath
from pathlib import Path
from shutil import copy2

import stringcase
from floxcore import CONFIG_DIRS
from floxcore.console import warning, error_box, prompt
from floxcore.context import Flox
from floxcore.remotes import universal_copy, generate_cache_hash
from jinja2 import Environment, FileSystemLoader
from loguru import logger


def _reload_cache(flox: Flox, cache_dir: str):
    if isdir(cache_dir):
        shutil.rmtree(cache_dir)

    for repository in flox.settings.bootstrap.repositories:
        universal_copy(flox, cache_dir, repository)


def load(path: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)

    return foo


def enable(flox: Flox, templates: tuple, no_cache: bool, out=None, **kwargs):
    """Bootstraps project with given templates"""
    cache_dir = CONFIG_DIRS.get_in("user", "templates-cache")
    out = out or logger

    if not len(flox.settings.bootstrap.repositories):
        error_box("Repositories not configured. Run: flox configure --plugin=bootstrap")
        return

    if no_cache or not isdir(cache_dir):
        _reload_cache(flox, cache_dir)

    existing_paths = []
    for template_name in templates:
        for repository in flox.settings.bootstrap.repositories:
            template_path = os.path.join(cache_dir, generate_cache_hash(repository), template_name, "template")
            if os.path.isdir(template_path):
                existing_paths.append(template_path)

    non_existing = set(templates) - set([Path(p).parts[-2] for p in existing_paths])
    for name in non_existing:
        warning(f'Bootstrap "{name}" does not exist')

    kwargs.update({
        "project_name": flox.name,
        "project_name_hyphen": stringcase.spinalcase(flox.name),
        "project_name_underscore": stringcase.snakecase(flox.name),
        "project_name_camel_case": stringcase.pascalcase(flox.name),
    })

    kwargs.update({f"project_{k}": v for k, v in flox.meta.all().items()})

    for template_path in existing_paths:
        name = Path(template_path).parts[-2]
        variables_file = abspath(join(template_path, "..", "variables.py"))
        if isfile(variables_file):
            logger.debug("Prompt for template variables")
            module = load(variables_file, f"{name}.variables")
            for var in module.VARIABLES:
                kwargs[f"{name}_{var.name}"] = prompt(var)

    generated = set()
    for template_path in existing_paths:
        name = Path(template_path).parts[-2]
        hooks_file = abspath(join(template_path, "..", "hooks.py"))
        module = OrderedDict()
        if isfile(hooks_file):
            logger.debug("Loading hooks")
            module = load(hooks_file, f"{name}.hooks")

        template_files = {k: str(k).replace(template_path, "").strip("/") for k in Path(template_path).glob("**/*")}

        if "pre_bootstrap" in module.__dict__:
            logger.debug(f"Calling pre_bootstrap hook for {name}")
            template_files = module.pre_bootstrap(template_files=template_files, features=templates, **kwargs)

        out.info(f"Bootstrapping project using template: {name}")
        env = Environment(loader=FileSystemLoader(template_path))

        logger.debug(f"Variables: {kwargs}")

        for absolute, relative in template_files.items():
            item_destination = os.path.join(flox.working_dir, relative)
            item_destination = re.sub(r"(<(.*?)>)", "{\\2}", item_destination).format(**kwargs)

            generated.add(item_destination.replace(".j2", ""))

            if os.path.isdir(str(absolute)):
                os.makedirs(item_destination, exist_ok=True)
            else:
                if not item_destination.endswith(".j2"):
                    copy2(str(absolute), item_destination)
                else:
                    template = env.get_template(relative)
                    template.stream(**kwargs).dump(item_destination.replace(".j2", ""))

        if "post_bootstrap" in module.__dict__:
            logger.debug(f"Calling post_bootstrap hook for {name}")
            module.post_bootstrap()

    return dict(
        bootstrap_generated=generated
    )
