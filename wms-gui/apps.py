import logging
import base64
import glob
import os
from contextlib import contextmanager
from subprocess import run, CalledProcessError

import streamlit as st
from logging import handlers

import yaml

# log = logging.getLogger(__name__)
# log = st.session_state.log
if "log" not in st.session_state:
    log = st.logger.get_logger('root')
    log.addHandler(handlers.SysLogHandler('/dev/log'))
    st.session_state['log'] = log
else:
    log = st.session_state.log

NotInstalled = 1
NotRunning = 2
Running = 3


def state_text(state):
    if state == NotInstalled:
        return "Not Installed"
    elif state == NotRunning:
        return "Not Running"
    elif state == Running:
        return "Running"
    else:
        return "Unknown"


@contextmanager
def pushd(new_dir):
    """A Python context to move in and out of directories"""
    previous_dir = os.getcwd()
    print(f"pushd: prev: {previous_dir} new: {new_dir}")
    os.chdir(new_dir)
    try:
        yield
    finally:
        print(f"pushd: popping back to prev: {previous_dir} new: {new_dir}")
        os.chdir(previous_dir)


# define a base class, so all have the same base set of methods
class AppBase(object):
    # Generic base class
    def __init__(self):
        pass

    def status(self):
        # returns status of the app (NotInstalled, NotRunning, Running)
        pass

    def install(self):
        # install the app
        pass

    def start(self):
        # start the app
        pass

    def stop(self):
        # stop the app
        pass

    def restart(self):
        # restart the app
        self.stop()
        self.start()

    def run(self, cmd, *args, capture_output=True, check=True, text=True, timeout=5, **kwargs):
        result=None
        log.debug(f'AppBase: Running {cmd}: {kwargs}')
        result = run(cmd, *args, capture_output=capture_output, check=check, text=text, timeout=timeout, **kwargs)
        log.debug(result)
        return result

class LocalWekaHome(AppBase):
    # Local Weka Home class
    def __init__(self):
        config_files = st.session_state.app_config.app_config['config_files']

        self.CONFIG = config_files['lwh_config_file']
        self.HELM = '/opt/wekahome/current/bin/helm'
        self.KUBECTL = '/opt/k3s/bin/kubectl'
        #self.CHECK_UP = [self.KUBECTL, 'wait', '--for=condition=ready', 'pod', '-l', 'app.group=common', '-n',
        #                 'home-weka-io', '--timeout=10m']
        # this returns something like 'wekahome.local   True'
        self.CHECK_UP = [self.KUBECTL, 'get', 'node', '--no-headers=true', '-o', 
                                'custom-columns=NODE_NAME:.metadata.name,STATUS:.status.conditions[?(@.type=="Ready")].status]']
        self.RM_KUBE_GRAFANA = [self.KUBECTL, 'delete', 'pod', '-n', 'home-weka-io', '-l',
                                'app.kubernetes.io/name=grafana']
        self.LWH_DIR = config_files['lwh_dir'] + '/current'
        tarball_list = glob.glob('/opt/wekahome*.bundle')
        if len(tarball_list) == 0:
            raise Exception(f'ERROR: File not found: {self.LWH_DIR}/wekahome*.bundle')
        elif len(tarball_list) != 1:
            raise Exception(f'ERROR: Too many files found: {tarball_list}')
        self.LWH_TARBALL = tarball_list[0]
        #self.UPDATE = [self.HELM, 'upgrade', 'homewekaio', '--namespace', 'home-weka-io', self.LWH_TARBALL,
        #               '--create-namespace', '-f', self.CONFIG, '--debug']
        #self.UPDATE = ['/opt/wekahome/current/bin/homecli', 'local', 'upgrade', '-c', 'config.json']

        split_filename = self.LWH_TARBALL.split('/')
        filename = split_filename[-1][:-7]  # trim off '.bundle'
        self.version = filename.split('-')[-1]
        # We'll make minikube a sub-part of LWH...
        #self.minikube = MiniKube()

        #cmd = ['bash', self.LWH_TARBALL]
        #result = self.run(cmd, timeout=30)

        super().__init__()

    def status(self):
        # returns status of the app (NotInstalled, NotRunning, Running)
        if not os.path.isfile(self.CONFIG) or not os.path.isfile(self.KUBECTL):
            return NotInstalled

        # if minikube isn't installed, LWH certainly isn't
        #minikube_status = self.minikube.status()
        #if minikube_status != Running:
        #    return minikube_status  # NotRunning or NotInstalled

        cmd = [self.KUBECTL, 'get', 'pods', '--namespace', 'home-weka-io']
        result = self.run(cmd, timeout=30)

        if len(result.stderr.splitlines()) > 0:
            log.debug(result.stderr)
            if result.stderr[:2] == 'No':
                return NotInstalled
        elif len(result.stdout.splitlines()) > 5:  # This should be fancier
            return Running
        else:
            return NotRunning

    def install(self):
        # install the app
        if self.status() != NotInstalled:
            raise Exception("LWH already installed")

        #if self.minikube.status() == NotInstalled:
        #    try:
        #        self.minikube.install()
        #    except Exception as exc:
        #        raise Exception(f'Minikube install failed: {exc}')

        #with pushd('/opt'):
        # so we've already asked if LWH is installed, so we can assume this file isn't there
        # shutil.copyfile(self.CUSTOMER_CONFIG_FILE, self.CONFIG)
        # run the install script
        #cmd = self.LWH_DIR + '/wekahome-install.sh'
        log.info("Installing LWH")
        lwh_config_file = st.session_state.app_config.app_config['config_files']['lwh_config_file']
        cmd = f'/opt/wekahome/current/bin/homecli local setup -c {lwh_config_file}'
        result = self.run(cmd, timeout=10 * 60, shell=True)
        if result.returncode != 0:
            log.critical(result.stdout)
            log.critical(result.stderr)
            raise Exception(f"Errors installing LWH")
        log.info("LWH installation succeeded")
        return True

    def update(self):
        # start the app

        log.info("updating LWH")
        try:
            lwh_config_file = st.session_state.app_config.app_config['config_files']['lwh_config_file']
            cmd = f'/opt/wekahome/current/bin/homecli local upgrade -c {lwh_config_file}'
            self.run(cmd, timeout=10*60, shell=True)
        except Exception as exc:
            log.critical(f'Local Weka Home update failed {exc}')
            raise Exception(f'Local Weka Home update failed {exc}')

        log.info("LWH update succeeded")
        return True

    def stop(self):
        # stop the app
        pass

    def admin_password(self):
        str_cmd = self.KUBECTL + \
                " get secret -n home-weka-io wekahome-admin-credentials  -o jsonpath='{.data.adminPassword}'"
                  #" get secret -n home-weka-io weka-home-admin-credentials  -o jsonpath='{.data.admin_password}'"
        result = self.run(str_cmd, shell=True)

        password = base64.b64decode(result.stdout)
        return password.decode('utf-8')

    def grafana_password(self):
        # str_cmd = "kubectl get secret -n home-weka-io weka-home-grafana-credentials  -o jsonpath='{.data.password}'"
        str_cmd = self.KUBECTL + \
                "  get secret -n home-weka-io wekahome-grafana-credentials  -o jsonpath='{.data.password}'"

        result = self.run(str_cmd, shell=True)
        password = base64.b64decode(result.stdout)
        return password.decode('utf-8')


# define a base class, so all have the same base set of methods
class WEKAmon(AppBase):
    # Generic base class
    def __init__(self):
        self.config_files = st.session_state.app_config.app_config['config_files']
        self.WEKAMON_DIR = self.config_files['weka_mon_dir']
        super().__init__()

    def status(self):
        # returns status of the app (NotInstalled, NotRunning, Running)
        log.info("running docker image list...")
        cmd = '/usr/bin/docker image list | grep wekasolutions'
        try:
            result = self.run(cmd, shell=True, timeout=30)
        except CalledProcessError:
            return NotInstalled  # grep will return 1 if no matches
        log.debug(result)

        # make sure there are wekasolutions container images (export, quota-export, hw_monitor, and snaptool)
        if len(result.stdout.splitlines()) < 1:
            return NotInstalled

        log.info("running docker compose ps")
        cmd = ['/usr/bin/docker', 'compose', 'ps']
        result = self.run(cmd)
        log.debug(result)

        # how to tell not installed?
        if len(result.stdout.splitlines()) == 1:
            # just the header printed... nothing in there
            return NotRunning
        else:
            # we should read the output to verify all are up and running...
            return Running

    def install(self):
        # install the app
        log.info("running install.sh")
        cmd = './install.sh'
        result = run(cmd, shell=True)
        log.info(result)

        log.info("running docker load")
        cmd = ['/usr/bin/docker', 'load', '-i', 'wekamon-containers.tgz']
        result = self.run(cmd, timeout=60)
        log.info(result)

    def start(self):
        # start the app
        log.info("running docker compose up")
        cmd = ['/usr/bin/docker', 'compose', 'up', '-d']
        result = self.run(cmd, timeout=60)
        log.debug(result)

    def stop(self):
        # stop the app
        log.info("running docker compose down")
        cmd = ['/usr/bin/docker', 'compose', 'down']
        result = self.run(cmd, timeout=60)
        log.debug(result)

    def is_running(self, container):
        result = self.run(f'docker compose ps --filter status=running | grep {container}', shell=True, check=False)
        return True if result.returncode == 0 else False

    def compose_ps(self):
        result = self.run('docker compose ps', shell=True, check=False)
        return result.stdout

    def run(self, cmd, *args, capture_output=True, check=True, text=True, timeout=5, **kwargs):
        # print(f'WEKAmon: Running {cmd}: {kwargs}')
        if 'cwd' not in kwargs:
            kwargs['cwd'] = self.WEKAMON_DIR
        with pushd(self.WEKAMON_DIR):
            return super().run(cmd, *args, capture_output=capture_output, check=check, text=text, timeout=timeout,
                               **kwargs)
        #return super().run(cmd, *args, capture_output=capture_output, check=check, text=text, timeout=timeout,
        print(result)
        # return result
