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
    context.group_sip_1 = context.settings['group_sip_1']
    context.group_sip_2 = context.settings['group_sip_2']
    context.group_sip_3 = context.settings['group_sip_3']
    context.group_sip_4 = context.settings['group_sip_4']
    context.group_sip_5 = context.settings['group_sip_5']
    context.group_sip_6 = context.settings['group_sip_6']
    context.group_sip_7 = context.settings['group_sip_7']
    context.group_sip_8 = context.settings['group_sip_8']
    context.sips = []
    for i in range(1, 9):
        context.sips.append(eval('context.group_sip_' + str(i)))