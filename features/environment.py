from yaml import load


def before_all(context):
    context.settings = load(open('features/conf.yml').read())
    context.base_url = context.settings["base_url"]
    context.component_installation_dir = context.settings[
        "component_installation_dir"]
    context.time_weight = context.settings["time_weight"]
    context.page_size_to_select_all = context.settings[
        "page_size_to_select_all"]
    context.token = None
    context.mysql_installation_dir = context.settings["mysql_installation_dir"]
