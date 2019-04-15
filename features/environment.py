from yaml import load


def before_all(context):
    ud = context.config.userdata
    context.base_url = ud.get("base_url")
    context.component_installation_dir = ud.get(
        "component_installation_dir")
    #context.time_weight = ud.get("time_weight")
    context.time_weight = int(ud.get("time_weight"))
    context.page_size_to_select_all = ud.get(
        "page_size_to_select_all")
    context.token = None
    context.mysql_installation_dir = ud.get("mysql_installation_dir")
    context.group_sip_1 = ud.get('group_sip_1')
    context.group_sip_2 = ud.get('group_sip_2')
    context.group_sip_3 = ud.get('group_sip_3')
    context.group_sip_4 = ud.get('group_sip_4')
    context.group_sip_5 = ud.get('group_sip_5')
    context.group_sip_6 = ud.get('group_sip_6')
    context.group_sip_7 = ud.get('group_sip_7')
    context.group_sip_8 = ud.get('group_sip_8')
    context.sips = []
    for i in range(1, 9):
        context.sips.append(eval('context.group_sip_' + str(i)))