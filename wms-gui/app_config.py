import glob
import json
import os

import yaml
import streamlit as st


# import subprocess

lwh_config_read = False
clusters_read = False
# log = logging.getLogger(__name__)
log = st.session_state.log

"""
PASSWD_CMD = '/usr/bin/passwd'


def set_password(user, password):
    cmd = ["sudo", PASSWD_CMD, '--stdin', user]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    # p.stdin.write(u'%(p)s\n%(p)s\n' % {'p': password})
    p.stdin.write(f"{password}")
    p.stdin.flush()
    # Give `passwd` cmd 1 second to finish and kill it otherwise.
    for x in range(0, 10):
        if p.poll() is not None:
            break
        sleep(0.1)
    else:
        p.terminate()
        sleep(1)
        p.kill()
        raise RuntimeError('Setting password failed. '
                           '`passwd` process did not terminate.')
    if p.returncode != 0:
        raise RuntimeError('`passwd` failed: %d' % p.returncode)
"""


def expand_directory(directory):
    dir_list = glob.glob(directory)
    if len(dir_list) != 1:
        raise Exception(f"ERROR searching for {directory} directory.  {dir_list}")
    return dir_list[0]


class AppConfig(object):
    def __init__(self, config_file):
        self.config_file = config_file
        self.api = None
        self.tokens = None
        with open(config_file, 'r') as f:
            self.app_config = yaml.safe_load(f)
        self.configs_loaded = False
        self.passwords_config = None
        self.lwh_config = None
        self.clusters_config = None
        self.export_config = None
        self.quota_export_config = None
        self.snaptool_config = None
        self.smtp_config = None
        self.enable_export = None
        self.enable_alerts = None
        self.enable_quota = None
        self.enable_snaptool = None
        self.enable_loki = None
        self.compose_file = None
        self.compose_dir = None

    def load_configs(self):
        try:
            if not self.configs_loaded:
                config_files = self.app_config['config_files']
                with open(config_files['passwords_file'], 'r') as f:
                    self.passwords_config = yaml.safe_load(f)
                with open(config_files['lwh_config_file'], 'r') as f:
                    self.lwh_config = yaml.safe_load(f)
                with open(config_files['clusters_config_file'], 'r') as f:
                    self.clusters_config = yaml.safe_load(f)
                with open(config_files['export_config_file'], 'r') as f:
                    self.export_config = yaml.safe_load(f)
                with open(config_files['quota_export_config_file'], 'r') as f:
                    self.quota_export_config = yaml.safe_load(f)
                with open(config_files['snaptool_config_file'], 'r') as f:
                    self.snaptool_config = yaml.safe_load(f)
                with open(config_files['email_settings_file'], 'r') as f:
                    self.smtp_config = yaml.safe_load(f)
                self.enable_export = config_files['enable_export']
                self.enable_alerts = config_files['enable_alerts']
                self.enable_quota = config_files['enable_quota']
                self.enable_snaptool = config_files['enable_snaptool']
                self.enable_loki = config_files['enable_loki']
                #with open(config_files['compose_file'], 'r') as f:
                #    self.compose_file = yaml.safe_load(f)
                self.compose_file = config_files['compose_file']
                self.compose_dir = config_files['compose_dir']

                self.configs_loaded = True
        except Exception as exc:
            print(f"load_configs: raising exception {exc}")
            raise

    def save_configs(self):
        # don't save if we haven't loaded yet!
        if self.configs_loaded:
            config_files = self.app_config['config_files']
            config_files['enable_export'] = self.enable_export
            config_files['enable_alerts'] = self.enable_alerts
            config_files['enable_quota'] = self.enable_quota
            config_files['enable_snaptool'] = self.enable_snaptool
            config_files['enable_loki'] = self.enable_loki
            with open(self.config_file, 'w') as f:
                yaml.dump(self.app_config, f, default_flow_style=False, sort_keys=False)

    def save_smtp(self):
        config_files = self.app_config['config_files']
        with open(config_files['email_settings_file'], 'w') as file:
            return yaml.dump(self.smtp_config, file, default_flow_style=False)

    def save_passwords(self):
        config_files = self.app_config['config_files']
        with open(config_files['passwords_file'], 'w') as file:
            return yaml.dump(self.passwords_config, file, default_flow_style=False)

    def save_lwh_config(self):
        config_files = self.app_config['config_files']
        with open(config_files['lwh_config_file'], 'w') as file:
            return yaml.dump(self.lwh_config, file, default_flow_style=False, sort_keys=False)

    def update_tokens(self, weka_api, tokens):
        self.api = weka_api
        self.tokens = tokens

    def save_clusters(self):
        config_files = self.app_config['config_files']
        with open(config_files['clusters_config_file'], 'w') as file:
            yaml.dump(self.clusters_config, file, default_flow_style=False)

        print('updating cluster dicts')
        self.update_cluster_dict(self.export_config)
        self.update_cluster_dict(self.quota_export_config)
        self.update_cluster_dict(self.snaptool_config)

        print('updating config files')
        self.update_export()
        self.update_quota_export()
        self.update_snaptool()

        print('writing security tokens')
        self.save_auth_tokens(os.path.dirname(config_files['export_config_file']))
        self.save_auth_tokens(os.path.dirname(config_files['quota_export_config_file']))
        self.save_auth_tokens(os.path.dirname(config_files['snaptool_config_file']))

        print('save complete')

    def update_config(self, filename, config):
        # expanded = expand_directory(directory)
        # self.save_auth_tokens(expanded)
        # config_file = os.path.join(expanded, filename)
        # config = None
        # with open(filename, 'r') as f:
        #    config = yaml.load(f, Loader=SafeLoader)
        # if config is None:
        #    raise Exception(f"Failed to open {filename}")
        # self.update_cluster_dict(config)
        if len(config) == 0:
            print('config is zero length!')
            return
        with open(filename, 'w') as f:
            yaml.safe_dump(config, f, indent=4)

    def save_auth_tokens(self, directory):
        if self.tokens is not None:
            wekadir = os.path.join(directory, '.weka')
            try:
                os.mkdir(wekadir)
            except FileExistsError:
                pass
            except FileNotFoundError:
                raise Exception(f"{directory} not found")
            with open(os.path.join(wekadir, 'auth-token.json'), 'w') as f:
                json.dump(self.tokens, f, indent=4)

    def update_cluster_dict(self, config):
        hosts = self.api.get_hosts()
        hostnames = list()
        for host in hosts['data'][:3]:  # only the first 3
            hostnames.append(str(host['name']))
        config['cluster']['hosts'] = hostnames

    def update_export(self):
        if self.enable_loki:
            self.export_config['exporter']['loki_host'] = 'loki'
        else:
            self.export_config['exporter']['loki_host'] = ''
        self.update_config(self.app_config['config_files']['export_config_file'], self.export_config)

    def update_quota_export(self):
        self.update_config(self.app_config['config_files']['quota_export_config_file'], self.quota_export_config)

    def update_snaptool(self):
        self.update_config(self.app_config['config_files']['snaptool_config_file'], self.snaptool_config)

    def configure_compose(self):
        # build docker-compose configuration file
        compose_config = {'version': "3", 'services': dict()}
        services = compose_config['services']

        log.info('Generating compose configuration')

        add_grafana = False
        add_prometheus = False
        add_alertmanager = False

        def load_config(services, name):
            with open(f'{self.compose_dir}/{name}.yml') as f:
                services[name] = yaml.safe_load(f)

        if self.enable_export:
            log.info('enabling export')
            load_config(services, "export")
            add_grafana = True
            add_prometheus = True
        if self.enable_alerts:
            add_alertmanager = True     # maybe...
        if self.enable_loki:
            log.info('enabling loki')
            load_config(services, "loki")
            add_prometheus = True
        if self.enable_quota:
            log.info('enabling quota')
            load_config(services, "quota")
            add_prometheus = True
            add_alertmanager = True
        if self.enable_snaptool:
            log.info('enabling snaptool')
            load_config(services, "snaptool")

        if add_grafana:
            log.info('enabling grafana')
            load_config(services, "grafana")
        if add_prometheus:
            log.info('enabling prometheus')
            load_config(services, "prometheus")
        if add_alertmanager:
            log.info('enabling alertmanager')
            load_config(services, "alertmanager")

        with open(self.compose_file, "w") as f:
            yaml.dump(compose_config, f, default_flow_style=False, sort_keys=False)
        # Save the settings
        self.save_configs()