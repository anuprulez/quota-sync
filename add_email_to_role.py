import datetime
import os
import yaml

from bioblend import galaxy
from datetime import timedelta
from dateutil.parser import parse

config_file = "config_file.yaml"
gpu_access_role = "access_gpu_jupyterlab"
gpu_access_group = "access_gpu_jupyterlab"


with open(config_file, 'r') as handle:
    CONFIG = yaml.safe_load(handle)

with open(CONFIG['filename'], 'r') as handle:
    data = [x.split('\t') for x in handle.read().split('\n')[1:]]

gi = galaxy.GalaxyInstance(url=CONFIG['url'], key=CONFIG['key'])

print(CONFIG)
print(data)
print(gi)


def add_users():
    # find role
    rc = galaxy.roles.RolesClient(gi)
    all_roles = rc.get_roles()
    gpu_role = None
    for item in enumerate(all_roles):
        if item[1]["name"] == gpu_access_role:
            gpu_role = item
            break

    # get users
    l_user_ids = list()
    uc = galaxy.users.UserClient(gi)
    for i, item in enumerate(data):
        user = uc.get_users(f_email=item[1])
        l_user_ids.append(user[0]["id"])

    # create or update a group
    gc = galaxy.groups.GroupsClient(gi)
    all_groups = gc.get_groups()
    gpu_group = None
    for gp in all_groups:
        if gp["name"] == gpu_access_group:
            gpu_group = gp
            break

    gc.update_group(group_id=gpu_group["id"], user_ids=l_user_ids, role_ids=[gpu_role[1]["id"]])


add_users()

