import requests
import time


_Debug = False


def find_running_server(api_token, expected_slug=None):
    running_server = None
    attempts = 0
    while attempts < 50:
        attempts += 1
        servers_response = requests.get(
            url='https://api.webdock.io/v1/servers',
            headers={
                'Authorization': f'Bearer {api_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
        )
        if _Debug:
            print(f'webdock_io.find_running_server GET:/v1/servers response: {servers_response.text}\n')
        servers_response.raise_for_status()
        servers_list = servers_response.json()
        if not servers_list:
            return None

        first_pending_server = None
        for srv in servers_list:
            if expected_slug:
                if expected_slug != srv['slug']:
                    continue
            if srv.get('status') == 'running':
                running_server = srv
                break
            if srv.get('status') in ['provisioning', 'rebooting', 'starting', 'reinstalling', ]:
                first_pending_server = srv
                break

        if running_server:
            break

        if first_pending_server:
            time.sleep(5)
            continue

        break

    return running_server


def find_stopped_server(api_token):
    stopped_server = None
    attempts = 0
    while attempts < 10:
        attempts += 1
        servers_response = requests.get(
            url='https://api.webdock.io/v1/servers',
            headers={
                'Authorization': f'Bearer {api_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
        )
        if _Debug:
            print(f'webdock_io.find_stopped_server GET:/v1/servers response: {servers_response.text}\n')
        servers_response.raise_for_status()
        servers_list = servers_response.json()
        if not servers_list:
            return None

        first_pending_server = None
        for srv in servers_list:
            if srv.get('status') == 'stopped':
                stopped_server = srv
                break
            if srv.get('status') in ['provisioning', 'rebooting', 'starting', 'reinstalling', 'stopping', ]:
                first_pending_server = srv
                break

        if stopped_server:
            break

        if first_pending_server:
            time.sleep(5)
            continue

        break

    return stopped_server


def start_stopped_server(api_token, server_info):
    server_slug = server_info.get('slug')
    if not server_slug:
        return
    server_start_response = requests.post(
        url=f'https://api.webdock.io/v1/servers/{server_slug}/actions/start',
        headers={
            'Authorization': f'Bearer {api_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
    )
    if _Debug:
        print(f'webdock_io.find_stopped_server POST:/v1/servers/{server_slug}/actions/start response: {server_start_response.text}\n')
    server_start_response.raise_for_status()


def deploy_new_server(api_token):
    locations_response = requests.get(
        url='https://api.webdock.io/v1/locations',
        headers={
            'Authorization': f'Bearer {api_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
    )
    if _Debug:
        print(f'webdock_io.deploy_new_server GET:/v1/locations response: {locations_response.text}\n')
    locations_response.raise_for_status()
    locations_list = locations_response.json()
    if not locations_list:
        raise Exception('not possible to deploy a new server, fetching available locations has failed')
    location_id = locations_list[0]['id']

    profiles_response = requests.get(
        url=f'https://api.webdock.io/v1/profiles?locationId={location_id}',
        headers={
            'Authorization': f'Bearer {api_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
    )
    if _Debug:
        print(f'webdock_io.deploy_new_server GET:/v1/profiles?locationId={location_id} response: {profiles_response.text}\n')
    profiles_response.raise_for_status()
    profiles_list = profiles_response.json()
    if not profiles_list:
        raise Exception('not possible to deploy a new server, fetching available profiles has failed')

    selected_profile_slug = None
    for prof in profiles_list:
        if prof['slug'].count('webdocknano'):
            selected_profile_slug = prof['slug']
            break
    if not selected_profile_slug:
        selected_profile_slug = profiles_list[0]['slug']

    images_response = requests.get(
        url='https://api.webdock.io/v1/images',
        headers={
            'Authorization': f'Bearer {api_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
    )
    if _Debug:
        print(f'webdock_io.deploy_new_server GET:/v1/images response: {images_response.text}\n')
    images_response.raise_for_status()
    images_list = images_response.json()
    if not images_list:
        raise Exception('not possible to deploy a new server, fetching available images has failed')
    selected_image_slug = ''
    for image_info in images_list:
        if image_info.get('webServer') or image_info.get('phpVersion'):
            continue
        if image_info['name'].lower().count('ubuntu'):
            selected_image_slug = image_info['slug']
            break 

    if _Debug:
        print(f'location={location_id} profile={selected_profile_slug} image={selected_image_slug}')

    server_deploy_response = requests.post(
        url=f'https://api.webdock.io/v1/servers',
        data=None,
        json={
            'name': 'bitdust',
            'locationId': location_id,
            'profileSlug': selected_profile_slug,
            'imageSlug': selected_image_slug,
        },
        headers={
            'Authorization': f'Bearer {api_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
    )
    if _Debug:
        print(f'webdock_io.deploy_new_server POST:/v1/servers response: {server_deploy_response.text}\n')
    server_deploy_response.raise_for_status()
    new_server_info = server_deploy_response.json()
    time.sleep(5)

    running_server = find_running_server(api_token)
    if not running_server:
        raise Exception('server was deployed, but still not running')

    if running_server['slug'] != new_server_info['slug']:
        if _Debug:
            print('WARNING! multiple running servers discovered')

    return running_server


def check_start_deploy_server(api_token):
    running_server = find_running_server(api_token)
    if not running_server:
        stopped_server = find_stopped_server(api_token)
        if not stopped_server:
            running_server = deploy_new_server(api_token)
        else:
            start_stopped_server(api_token, stopped_server)
            time.sleep(5)
            running_server = find_running_server(api_token)
    if not running_server:
        raise Exception('deployment failed, no running servers found')
    return running_server


def check_create_update_scripts(api_token, server_alias):
    head_sh = '#!/bin/bash\r\n\r\nwhoami; pwd; id; '
    apt_sh = 'apt-get update; apt-get --yes install git gcc build-essential libssl-dev libffi-dev python3-dev python3-virtualenv; '
    useradd_sh = 'useradd -m -d /home/bitdust -s /bin/bash bitdust; usermod -aG sudo bitdust; '
    su_wrapper = lambda inp: f"su -c 'cd; whoami; pwd; id; {inp}' bitdust; "
    # clone_sh = 'rm -rf /home/bitdust/bitdust; git clone https://github.com/bitdust-io/public.git /home/bitdust/bitdust; '
    clone_sh = 'rm -rf /home/bitdust/bitdust; git clone https://github.com/vesellov/devel.git /home/bitdust/bitdust; '
    install_sh = 'cd /home/bitdust/bitdust; python3 bitdust.py install && export PATH=\"$PATH:/home/bitdust/.bitdust/\" && bitdust set debug 16 && '
    kill_sh = 'ps aux && bitdust kill && '
    start_sh = 'bitdust daemon && sleep 20 && bitdust states &&'
    add_device_sh = f"bitdust dev add direct client1 {server_alias} && bitdust dev stop client1 && bitdust dev key client1 && bitdust dev start client1 && "
    tail_sh = 'echo "\nSUCCESS\n"'
    bitdust_deploy_sh = head_sh + apt_sh + useradd_sh + su_wrapper(clone_sh + install_sh + kill_sh + start_sh + add_device_sh + tail_sh)
    # bitdust_deploy_sh = f"#!/bin/bash\r\n\r\nwhoami; pwd; id; apt-get update; apt-get --yes install git gcc build-essential libssl-dev libffi-dev python3-dev python3-virtualenv; useradd -m -d /home/bitdust -s /bin/bash bitdust; usermod -aG sudo bitdust; su -c 'cd; rm -rf bitdust; git clone https://github.com/bitdust-io/public.git bitdust; cd bitdust; python3 bitdust.py install && export PATH=\"$PATH:/home/bitdust/.bitdust/\" && bitdust set debug 16 && ps aux && bitdust kill && bitdust daemon && sleep 20 && bitdust states && bitdust dev add direct client1 {server_alias} && bitdust dev stop client1 && bitdust dev key client1 && bitdust dev start client1' bitdust;"

    existing_script = None
    scripts_response = requests.get(
        url='https://api.webdock.io/v1/account/scripts',
        headers={
            'Authorization': f'Bearer {api_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
    )
    if _Debug:
        print(f'webdock_io.check_create_scripts GET:/v1/account/scripts response: {scripts_response.text}\n')
    scripts_response.raise_for_status()
    scripts_list = scripts_response.json()
    for script_info in scripts_list:
        if script_info['name'] == 'bitdust_deploy':
            existing_script = script_info
            break

    if existing_script:
        script_update_response = requests.patch(
            url=f'https://api.webdock.io/v1/account/scripts/{existing_script["id"]}',
            data=None,
            json={
                'name': 'bitdust_deploy',
                'filename': 'bitdust_deploy.sh',
                'content': bitdust_deploy_sh,
            },
            headers={
                'Authorization': f'Bearer {api_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
        )
        if _Debug:
            print(f'webdock_io.check_create_update_scripts PATCH:/v1/account/scripts/{existing_script["id"]} response: {script_update_response.text}\n')
        script_update_response.raise_for_status()
        existing_script = script_update_response.json()

    else:
        script_create_response = requests.post(
            url=f'https://api.webdock.io/v1/account/scripts',
            data=None,
            json={
                'name': 'bitdust_deploy',
                'filename': 'bitdust_deploy.sh',
                'content': bitdust_deploy_sh,
            },
            headers={
                'Authorization': f'Bearer {api_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
        )
        if _Debug:
            print(f'webdock_io.check_create_update_scripts POST:/v1/account/scripts response: {script_create_response.text}\n')
        script_create_response.raise_for_status()
        existing_script = script_create_response.json()

    return existing_script


def execute_script(api_token, server_slug, script_id):
    script_execute_response = requests.post(
        url=f'https://api.webdock.io/v1/servers/{server_slug}/scripts',
        data=None,
        json={
            'scriptId': script_id,
            'path': '/root/bitdust_deploy.sh',
            'makeScriptExecutable': True,
            'executeImmediately': True,
        },
        headers={
            'Authorization': f'Bearer {api_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
    )
    if _Debug:
        print(f'webdock_io.execute_script POST:/v1/servers/{server_slug}/scripts response: {script_execute_response.text}\n')
    script_execute_response.raise_for_status()

    time.sleep(10)

    first_script_execution_event = None
    attempts = 0
    while attempts < 60:
        attempts += 1
        events_response = requests.get(
            url='https://api.webdock.io/v1/events?eventType=push-file',
            headers={
                'Authorization': f'Bearer {api_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
        )
        if _Debug:
            print(f'webdock_io.execute_script GET:/v1/events response: {len(events_response.text)} bytes\n')
        events_response.raise_for_status()
        events_list = events_response.json()
        if not events_list:
            raise Exception('deployment script execution failed, not possible to fetch events list')

        for e in events_list:
            if e.get('eventType') == 'push-file' and (e.get('action') or '').count('bitdust_deploy'):
                first_script_execution_event = e
                break

        if not first_script_execution_event:
            if _Debug:
                print(f'    no script execution results found yet\n')
            time.sleep(10)
            continue

        if first_script_execution_event.get('status') not in ['finished', 'error', ]:
            if _Debug:
                print(f'    status is {first_script_execution_event.get("status")}\n')
            time.sleep(10)
            continue

        break

    if not first_script_execution_event:
        raise Exception('deployment script execution failed, not possible to find script execution result')

    return first_script_execution_event['message']


def run(api_token):
    ping_response = requests.get(
        url='https://api.webdock.io/v1/ping',
        headers={
            'Authorization': f'Bearer {api_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
    )
    if _Debug:
        print(f'webdock_io.find_running_server GET:/v1/ping response: {ping_response.text}\n')
    ping_response.raise_for_status()
    
    running_server = check_start_deploy_server(api_token)

    existing_script = check_create_update_scripts(api_token, running_server['aliases'][0])

    result = execute_script(api_token, running_server['slug'], existing_script['id'])

    return result
