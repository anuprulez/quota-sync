import sys
import datetime
import os
import yaml

from bioblend import galaxy
from datetime import timedelta
from dateutil.parser import parse

config_file = "config_file.yaml"

# create a role and a group in Galaxy
gpu_access_role = "access_gpu_jupyterlab"
gpu_access_group = "access_gpu_jupyterlab_1"


with open(config_file, 'r') as handle:
    CONFIG = yaml.safe_load(handle)

with open(CONFIG['filename'], 'r') as handle:
    data = [x.split('\t') for x in handle.read().split('\n')[1:]]

gi = galaxy.GalaxyInstance(url=CONFIG['url'], key=CONFIG['key'])


def add_users():
    
    print(data)
    
    approved_user_ids = list()
    for idx, (submit_date, email, name, institution, agreement, date_approved) in enumerate(data):
        date_approved = date_approved.strip()
        if len(date_approved) == 0:
            print("Skipping %s due to unapproved" % name)
            continue
        approved_user_ids.append(email)
    print(approved_user_ids)
    
    # find role
    rc = galaxy.roles.RolesClient(gi)
    gc = galaxy.groups.GroupsClient(gi)
    uc = galaxy.users.UserClient(gi)
    
    all_groups = gc.get_groups()
    gpu_group = None
    for gp in all_groups:
        if gp["name"] == gpu_access_group:
            gpu_group = gp
            break
    
    all_added_users = gc.get_group_users(group_id=gpu_group["id"])
        
    print("all_added_users", all_added_users)
    print()
    
    new_users = list(set(approved_user_ids).difference(set([item["email"] for item in all_added_users])))
    print("new_users", new_users)
    
    #sys.exit()
    l_user_ids = list()
    
    # get user ids
    for i, item in enumerate(new_users):
        user = uc.get_users(f_email=item)
        print(item, user)
        l_user_ids.append(user[0]["id"])

    # create or update a group
    all_roles = rc.get_roles()
    gpu_role = None
    for item in enumerate(all_roles):
        if item[1]["name"] == gpu_access_role:
            gpu_role = item
            break
            
    gc.update_group(group_id=gpu_group["id"], user_ids=l_user_ids, role_ids=[gpu_role[1]["id"]])

add_users()
