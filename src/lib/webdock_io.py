import platform
import requests
import time


_Debug = False


def find_running_server(api_token, expected_slug=None, cb_progress=None, cb_check_stopped=None):
    if cb_check_stopped and cb_check_stopped():
        if _Debug:
            print('\nSTOPPED!\n')
        raise Exception('stopped')
    if cb_progress:
        cb_progress('verify server is running ')

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
            if cb_check_stopped and cb_check_stopped():
                if _Debug:
                    print('\nSTOPPED!\n')
                raise Exception('stopped')
            if cb_progress:
                cb_progress('.')
            time.sleep(3)
            continue

        break

    if cb_progress:
        cb_progress(f'\n')

    if cb_check_stopped and cb_check_stopped():
        if _Debug:
            print('\nSTOPPED!\n')
        raise Exception('stopped')
    if cb_progress:
        cb_progress(f'found running VPS\n' if running_server else 'VPS is not running at the moment\n')

    return running_server


def find_stopped_server(api_token, cb_progress=None, cb_check_stopped=None):
    if cb_check_stopped and cb_check_stopped():
        if _Debug:
            print('\nSTOPPED!\n')
        raise Exception('stopped')
    if cb_progress:
        cb_progress('check if server was stopped ')

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
            if cb_check_stopped and cb_check_stopped():
                if _Debug:
                    print('\nSTOPPED!\n')
                raise Exception('stopped')
            if cb_progress:
                cb_progress('.')
            time.sleep(3)
            continue

        break

    if cb_progress:
        cb_progress(f'\n')

    if cb_check_stopped and cb_check_stopped():
        if _Debug:
            print('\nSTOPPED!\n')
        raise Exception('stopped')
    if cb_progress:
        cb_progress(f'found stopped VPS\n' if stopped_server else 'active server was not found\n')

    return stopped_server


def start_stopped_server(api_token, server_info, cb_progress=None, cb_check_stopped=None):
    server_slug = server_info.get('slug')
    if not server_slug:
        return

    if cb_check_stopped and cb_check_stopped():
        if _Debug:
            print('\nSTOPPED!\n')
        raise Exception('stopped')
    if cb_progress:
        cb_progress(f'starting the server\n')

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


def deploy_new_server(api_token, cb_progress=None, cb_check_stopped=None):
    if cb_check_stopped and cb_check_stopped():
        if _Debug:
            print('\nSTOPPED!\n')
        raise Exception('stopped')
    if cb_progress:
        cb_progress(f'reading available locations\n')

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
        raise Exception('not possible to deploy a new server, failed reading available locations')
    location_id = locations_list[0]['id']

    if cb_check_stopped and cb_check_stopped():
        if _Debug:
            print('\nSTOPPED!\n')
        raise Exception('stopped')
    if cb_progress:
        cb_progress(f'{locations_list[0]["description"].replace("Server", "server")}\n')
    if cb_progress:
        cb_progress(f'reading hardware profiles in {locations_list[0]["country"]}\n')

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
        raise Exception('not possible to deploy a new server, failed reading available hardware profiles')

    cheapest_by_currency = {}
    for prof in profiles_list:
        currency = prof['price']['currency']
        price = prof['price']['amount']
        if currency not in cheapest_by_currency:
            cheapest_by_currency[currency] = prof
        if cheapest_by_currency[currency]['price']['amount'] > price:
            cheapest_by_currency[currency] = prof
    if not cheapest_by_currency:
        raise Exception('no profiles found')

    selected_profile = list(cheapest_by_currency.values())[0]
    selected_profile_slug = selected_profile['slug']

    if cb_check_stopped and cb_check_stopped():
        if _Debug:
            print('\nSTOPPED!\n')
        raise Exception('stopped')
    if cb_progress:
        cb_progress(f'selected {selected_profile["name"]} which is {selected_profile["price"]["amount"] / 100.0} {selected_profile["price"]["currency"]} per month\n')

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
        raise Exception('not possible to deploy a new server, failed reading available images')
    selected_image_slug = ''
    selected_image = None
    for image_info in images_list:
        if image_info.get('webServer') or image_info.get('phpVersion'):
            continue
        if image_info['name'].lower().count('ubuntu'):
            selected_image_slug = image_info['slug']
            selected_image = image_info
            break

    if cb_check_stopped and cb_check_stopped():
        if _Debug:
            print('\nSTOPPED!\n')
        raise Exception('stopped')
    if cb_progress:
        cb_progress(f'started deployment of {selected_image["name"]} server\n')

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

    if cb_check_stopped and cb_check_stopped():
        if _Debug:
            print('\nSTOPPED!\n')
        raise Exception('stopped')
    if cb_progress:
        cb_progress(f'verifying current server status\n')

    time.sleep(3)

    running_server = find_running_server(api_token, cb_progress=cb_progress, cb_check_stopped=cb_check_stopped)
    if not running_server:
        raise Exception('server was deployed, but still not running')

    if running_server['slug'] != new_server_info['slug']:
        if _Debug:
            print('WARNING! multiple running servers discovered')

    return running_server


def check_start_deploy_server(api_token, cb_progress=None, cb_check_stopped=None):
    running_server = find_running_server(api_token, cb_progress=cb_progress, cb_check_stopped=cb_check_stopped)
    if not running_server:
        stopped_server = find_stopped_server(api_token, cb_progress=cb_progress, cb_check_stopped=cb_check_stopped)
        if not stopped_server:
            running_server = deploy_new_server(api_token, cb_progress=cb_progress, cb_check_stopped=cb_check_stopped)
        else:
            start_stopped_server(api_token, stopped_server, cb_progress=cb_progress, cb_check_stopped=cb_check_stopped)
            time.sleep(5)
            running_server = find_running_server(api_token, cb_progress=cb_progress, cb_check_stopped=cb_check_stopped)
    if not running_server:
        raise Exception('deployment failed, no running servers found')
    return running_server


def check_create_update_scripts(api_token, server_info, cb_progress=None, cb_check_stopped=None):
    server_alias = server_info['aliases'][0]
    server_slug = server_info['slug']
    client_dev_name = f'{platform.node()}_at_{server_slug}'.replace('-', '_').replace('$', '_').replace('%', '_').replace('&', '_').replace('*', '_').replace('+', '_')
    client_dev_name = client_dev_name[:20]
    head_sh = '#!/bin/bash\r\n\r\nwhoami; pwd; id; '
    apt_sh = 'apt-get update; apt-get --yes install git gcc build-essential libssl-dev libffi-dev python3-dev python3-virtualenv; '
    useradd_sh = 'useradd -m -d /home/bitdust -s /bin/bash bitdust; usermod -aG sudo bitdust; '
    su_wrapper = lambda inp: f"su -c 'cd; whoami; pwd; id; {inp}' bitdust; "
    # clone_sh = 'rm -rf /home/bitdust/bitdust; git clone https://github.com/bitdust-io/public.git /home/bitdust/bitdust; '
    clone_sh = 'rm -rf /home/bitdust/bitdust; git clone https://github.com/vesellov/devel.git /home/bitdust/bitdust; '
    install_sh = 'cd /home/bitdust/bitdust; python3 bitdust.py install && cd /home/bitdust/ && export PATH="$PATH:/home/bitdust/.bitdust" && '
    set_path_sh = '( ( grep -qxF "export PATH=\$PATH:/home/bitdust/.bitdust" .bashrc || echo "export PATH=\$PATH:/home/bitdust/.bitdust" >> .bashrc ) ) && '
    crontab_sh = 'bitdust install crontab && '
    kill_sh = 'bitdust kill && '
    start_sh = 'bitdust daemon && sleep 10 && bitdust states && '
    config_sh = 'bitdust set services/proxy-transport/enabled false && '
    add_device_sh = f"bitdust dev add direct {client_dev_name} {server_alias} && bitdust dev stop {client_dev_name} && bitdust dev key {client_dev_name} && bitdust dev start {client_dev_name} && "
    tail_sh = 'sleep 2 && bitdust restart && echo "" && echo "SUCCESS"'
    bitdust_deploy_sh = head_sh + apt_sh + useradd_sh + su_wrapper(clone_sh + install_sh + set_path_sh + crontab_sh + kill_sh + config_sh + start_sh + add_device_sh + tail_sh)

    if cb_check_stopped and cb_check_stopped():
        if _Debug:
            print('\nSTOPPED!\n')
        raise Exception('stopped')
    if cb_progress:
        cb_progress(f'prepare installation scripts\n')

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
        if cb_check_stopped and cb_check_stopped():
            if _Debug:
                print('\nSTOPPED!\n')
            raise Exception('stopped')
        if cb_progress:
            cb_progress(f'updating existing script content\n')

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
        if cb_check_stopped and cb_check_stopped():
            if _Debug:
                print('\nSTOPPED!\n')
            raise Exception('stopped')
        if cb_progress:
            cb_progress(f'uploading new installation script\n')

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


def execute_script(api_token, server_slug, script_id, cb_progress=None, cb_check_stopped=None):
    if cb_check_stopped and cb_check_stopped():
        if _Debug:
            print('\nSTOPPED!\n')
        raise Exception('stopped')
    if cb_progress:
        cb_progress(f'node installation .')

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

    time.sleep(3)

    first_script_execution_event = None
    attempts = 0
    while attempts < 50:
        if cb_check_stopped and cb_check_stopped():
            if _Debug:
                print('\nSTOPPED!\n')
            raise Exception('stopped')
        if cb_progress:
            cb_progress(f'.')

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
            print(f'webdock_io.execute_script GET:/v1/events?eventType=push-file response: {len(events_response.text)} bytes\n')
        events_response.raise_for_status()
        events_list = events_response.json()
        if not events_list:
            raise Exception('deployment script execution failed, not possible to fetch events list')

        if cb_check_stopped and cb_check_stopped():
            if _Debug:
                print('\nSTOPPED!\n')
            raise Exception('stopped')

        for e in events_list:
            if e.get('eventType') == 'push-file' and (e.get('action') or '').count('bitdust_deploy'):
                first_script_execution_event = e
                break

        if not first_script_execution_event:
            if _Debug:
                print(f'    no script execution results found yet\n')
            time.sleep(3)
            continue

        if _Debug:
            print(f'    status is {first_script_execution_event.get("status")}\n')
        if first_script_execution_event.get('status') not in ['finished', 'error', ]:
            time.sleep(3)
            continue

        break

    if cb_progress:
        cb_progress(f'\n')

    if not first_script_execution_event:
        raise Exception('deployment script execution failed, not possible to find script execution result')

    return first_script_execution_event


def run(api_token, cb_progress=None, cb_check_stopped=None):
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

    if cb_check_stopped and cb_check_stopped():
        if _Debug:
            print('\nSTOPPED!\n')
        raise Exception('stopped')
    if cb_progress:
        cb_progress('connecting to api.webdock.io\n')

    running_server = check_start_deploy_server(api_token, cb_progress=cb_progress, cb_check_stopped=cb_check_stopped)

    if cb_check_stopped and cb_check_stopped():
        if _Debug:
            print('\nSTOPPED!\n')
        raise Exception('stopped')

    existing_script = check_create_update_scripts(api_token, running_server, cb_progress=cb_progress, cb_check_stopped=cb_check_stopped)

    if cb_check_stopped and cb_check_stopped():
        if _Debug:
            print('\nSTOPPED!\n')
        raise Exception('stopped')

    result_info = execute_script(api_token, running_server['slug'], existing_script['id'], cb_progress=cb_progress, cb_check_stopped=cb_check_stopped)

    if result_info.get('status') != 'finished' or not (result_info.get('message') or '').strip().endswith('SUCCESS'):
        raise Exception(result_info.get('message') or 'script execution failed')

    if cb_progress:
        cb_progress(f'node was successfully configured\n')

    return result_info.get('message')
