import glob
import json
import logging
import os

import yaml

# import subprocess

lwh_config_read = False
clusters_read = False
# log = logging.getLogger(__name__)
# log = st.session_state.log

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
                self.configs_loaded = True
        except Exception as exc:
            print(f"load_configs: raising exception {exc}")
            raise

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
            return yaml.dump(self.lwh_config, file, default_flow_style=False)

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
        #self.update_config(config_files['export_config_file'], self.export_config)
        #self.update_config(config_files['quota_export_config_file'], self.quota_export_config)
        #self.update_config(config_files['snaptool_config_file'], self.snaptool_config)

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
        for host in hosts['data']:
            hostnames.append(str(host['name']))
        config['cluster']['hosts'] = hostnames

    def update_export(self):
        self.update_config(self.app_config['config_files']['export_config_file'], self.export_config)

    def update_quota_export(self):
        self.update_config(self.app_config['config_files']['quota_export_config_file'], self.quota_export_config)

    def update_snaptool(self):
        self.update_config(self.app_config['config_files']['snaptool_config_file'], self.snaptool_config)

