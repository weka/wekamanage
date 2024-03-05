import glob
import json
import os

import yaml
import json
import streamlit as st

from logging import handlers

# import subprocess

# log = logging.getLogger(__name__)
# log = st.session_state.log
if "log" not in st.session_state:
    log = st.logger.get_logger('root')
    log.addHandler(handlers.SysLogHandler('/dev/log'))
    st.session_state['log'] = log
else:
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


def expand_directory(directory):
    dir_list = glob.glob(directory)
    if len(dir_list) != 1:
        raise Exception(f"ERROR searching for {directory} directory.  {dir_list}")
    return dir_list[0]
"""


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
        self.alertmanager_config = None
        self.smtp_config = None
        self.prom_config = None
        self.hw_mon_config = None
        self.prometheus_dir = None
        self.enable_export = None
        self.enable_alerts = None
        self.enable_quota = None
        self.enable_snaptool = None
        self.enable_loki = None
        self.enable_hw_mon = None
        self.compose_file = None
        self.compose_dir = None
    
    def load_file(self, config_files, name):
        try:
            with open(config_files[name], 'r') as f:
                if config_files[name].split('.')[-1] == 'yml':
                    return yaml.safe_load(f)
                elif config_files[name].split('.')[-1] == 'json':
                    return json.load(f)
                log.error(f"load_file: unknown file type: {config_files[name]}")
        except FileNotFoundError:
            log.error(f"load_file: {config_files[name]} not found")
        except Exception as exc:
            log.error(f'load_file: ERROR {exc}')
            raise exc
        return None

    def load_configs(self):
        try:
            if not self.configs_loaded:
                config_files = self.app_config['config_files']
                self.passwords_config = self.load_file(config_files, 'passwords_file')
                self.lwh_config = self.load_file(config_files, 'lwh_config_file')
                self.clusters_config = self.load_file(config_files, 'clusters_config_file')
                self.export_config = self.load_file(config_files, 'export_config_file')
                self.quota_export_config = self.load_file(config_files, 'quota_export_config_file')
                self.snaptool_config = self.load_file(config_files, 'snaptool_config_file')
                self.alertmanager_config = self.load_file(config_files, 'alertmanager_config_file')
                self.smtp_config = self.load_file(config_files, 'email_settings_file')
                self.prom_config = self.load_file(config_files, 'prometheus_config_file')
                self.hw_mon_config = self.load_file(config_files, 'hw_mon_config_file')

                self.prometheus_dir = config_files['prometheus_dir']
                self.enable_export = config_files['enable_export']
                self.enable_alerts = config_files['enable_alerts']
                self.enable_quota = config_files['enable_quota']
                self.enable_snaptool = config_files['enable_snaptool']
                self.enable_loki = config_files['enable_loki']
                self.enable_hw_mon = config_files['enable_hw_mon']
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
            config_files['enable_hw_mon'] = self.enable_hw_mon
            with open(self.config_file, 'w') as f:
                yaml.dump(self.app_config, f, default_flow_style=False, sort_keys=False)

    def save_smtp(self):
        config_files = self.app_config['config_files']
        # update the lwh and alertmanager config files?
        lwh_smtp = self.lwh_config['smtp']
        lwh_smtp['senderEmail'] = self.smtp_config['sender_email']
        lwh_smtp['sender'] = self.smtp_config['sender_email_name']
        lwh_smtp['host'] = self.smtp_config['smtp_host']
        lwh_smtp['port'] = self.smtp_config['smtp_port']
        lwh_smtp['insecure'] = self.smtp_config['smtp_insecure_tls']
        lwh_smtp['password'] = self.smtp_config['smtp_password']
        lwh_smtp['user'] = self.smtp_config['smtp_username']
        self.save_lwh_config()

        alertmanager_smtp = self.alertmanager_config['global']
        alertmanager_smtp['smtp_smarthost'] = f"{self.smtp_config['smtp_host']}:{self.smtp_config['smtp_port']}"
        alertmanager_smtp['smtp_from'] = self.smtp_config['sender_email']
        alertmanager_smtp['smtp_auth_username'] = self.smtp_config['smtp_username']
        alertmanager_smtp['smtp_auth_identity'] = self.smtp_config['smtp_username']
        alertmanager_smtp['smtp_auth_password'] = self.smtp_config['smtp_password']
        alertmanager_smtp['smtp_require_tls'] = not self.smtp_config['smtp_insecure_tls']
        self.update_alertmanager()

        smtp_config = self.smtp_config
        smtp_config['smtp_password'] = ''   # don't save the password
        with open(config_files['email_settings_file'], 'w') as file:
            return yaml.dump(smtp_config, file, default_flow_style=False)

    def save_passwords(self):
        config_files = self.app_config['config_files']
        with open(config_files['passwords_file'], 'w') as file:
            return yaml.dump(self.passwords_config, file, default_flow_style=False)

    def save_lwh_config(self):
        config_files = self.app_config['config_files']
        with open(config_files['lwh_config_file'], 'w') as file:
            #return yaml.dump(self.lwh_config, file, default_flow_style=False, sort_keys=False)
            return json.dump(self.lwh_config, file, indent=4, sort_keys=False)

    def update_tokens(self, weka_api, tokens):
        self.api = weka_api
        self.tokens = tokens

    def save_clusters(self):
        config_files = self.app_config['config_files']
        clusters_config = self.clusters_config
        clusters_config['password'] = ""   # don't save the password
        with open(config_files['clusters_config_file'], 'w') as file:
            yaml.dump(clusters_config, file, default_flow_style=False)

        print('updating cluster dicts')
        self.update_cluster_dict(self.export_config)
        self.update_cluster_dict(self.quota_export_config)
        self.update_cluster_dict(self.snaptool_config)
        self.update_cluster_dict(self.hw_mon_config)

        print('updating config files')
        self.update_export()
        self.update_quota_export()
        self.update_snaptool()
        self.update_hw_mon()

        print('writing security tokens')
        self.save_auth_tokens(os.path.dirname(config_files['export_config_file']))
        self.save_auth_tokens(os.path.dirname(config_files['quota_export_config_file']))
        self.save_auth_tokens(os.path.dirname(config_files['snaptool_config_file']))
        self.save_auth_tokens(os.path.dirname(config_files['hw_mon_config_file']))

        print('save complete')

    def update_config(self, filename, config):
        if len(config) == 0:
            print('config is zero length!')
            return
        with open(filename, 'w') as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False, indent=4)

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
        hosts = self.api.get_base_containers()
        hostnames = list()
        for host in hosts[:3]:  # only the first 3
            hostnames.append(str(host['hostname']))
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

    def update_hw_mon(self):
        self.update_config(self.app_config['config_files']['hw_mon_config_file'], self.hw_mon_config)

    def update_alertmanager(self):
        self.update_config(self.app_config['config_files']['alertmanager_config_file'], self.alertmanager_config)

    def update_prometheus(self):
        self.update_config(self.app_config['config_files']['prometheus_config_file'], self.prom_config)

    def configure_prometheus(self):
        # set up the whole file from scratch
        log.info('Generating prometheus configuration')

        self.prom_config = dict()
        self.prom_config['global'] = {
            "evaluation_interval": "1m",
            "scrape_interval": "1m",
            "scrape_timeout": "50s",
        }

        self.prom_config['scrape_configs'] = list()
        scrape_configs = self.prom_config['scrape_configs']

        def load_config(config, name):
            print(f'loading prom config from dir {os.getcwd()}')
            with open(f'{self.prometheus_dir}/{name}.yml') as f:
                if type(config) == list:
                    config.append(yaml.safe_load(f))
                else:
                    config[name] = yaml.safe_load(f)

        # always add Prometheus (itself)
        load_config(scrape_configs, "prometheus")
        if self.enable_export:
            load_config(scrape_configs, "export")
            load_config(scrape_configs, "grafana")
        if self.enable_quota:
            load_config(scrape_configs, "quota-export")
            load_config(self.prom_config, "alerting")   # special case
            self.prom_config['rule_files'] = ["rules.yml"]       # special case
        if self.enable_loki:
            load_config(scrape_configs, "loki")
        #if self.enable_hw_mon:
        #    load_config(scrape_configs, "hw_mon")

        self.update_prometheus()
        # Save the settings
        self.save_configs()
        log.info('prometheus configuration complete')

    def configure_compose(self):
        # build docker-compose configuration file
        compose_config = {'version': "3", 'services': dict()}
        services = compose_config['services']

        log.info('Generating compose configuration')

        add_grafana = False
        add_prometheus = False
        add_alertmanager = False

        def load_config(services, name):
            print(f'loading config from dir {os.getcwd()}')
            with open(f'{self.compose_dir}/{name}.yml') as f:
                services[name] = yaml.safe_load(f)

        if self.enable_export:
            log.info('enabling export')
            load_config(services, "export")
            add_grafana = True
            add_prometheus = True
        if self.enable_loki:
            log.info('enabling loki')
            load_config(services, "loki")
            add_prometheus = True
        if self.enable_quota:
            log.info('enabling quota')
            load_config(services, "quota-export")
            add_prometheus = True
            add_alertmanager = True
        if self.enable_snaptool:
            log.info('enabling snaptool')
            load_config(services, "snaptool")
        if self.enable_hw_mon:
            log.info('enabling hw_mon')
            load_config(services, "hw_mon")

        if add_grafana:
            log.info('enabling grafana')
            load_config(services, "grafana")
        if add_prometheus:
            log.info('enabling prometheus')
            load_config(services, "prometheus")
        if add_alertmanager:
            log.info('enabling alertmanager')
            load_config(services, "alertmanager")
            # should probably set --web.external-url=<our url>:9093 - it's similar to LWH email link thing
            # should also have some setting of alertmanager notifiers similar to this model

        with open(self.compose_file, "w") as f:
            yaml.dump(compose_config, f, default_flow_style=False, sort_keys=False)
        # Save the settings
        self.save_configs()
        log.info('compose configuration complete')
