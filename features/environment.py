from yaml import load

def before_all(context):
    context.settings = load(open('features/conf.yml').read())
    context.base_url = context.settings["base_url"]
    context.component_installation_dir = context.settings["component_installation_dir"]
    context.time_weight = context.settings["time_weight"]
