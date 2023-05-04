import logging
import base64
import glob
import os
from contextlib import contextmanager
from subprocess import run, CalledProcessError

import streamlit as st
from logging import handlers

#log = logging.getLogger(__name__)
#log = st.session_state.log
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
    os.chdir(new_dir)
    try:
        yield
    finally:
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
        log.debug(f'AppBase: Running {cmd}: {kwargs}')
        result = run(cmd, *args, capture_output=capture_output, check=check, text=text, timeout=timeout, **kwargs)
        log.debug(result)
        return result


class MiniKube(AppBase):
    def __init__(self):

        # Minikube class
        self.KUBECTL = '/usr/bin/kubectl'
        self.MINIKUBE = '/usr/bin/minikube'
        self.GET_PODS = [self.KUBECTL] + ' get pods --namespace kube-system'.split()
        config_files = st.session_state.app_config.app_config['config_files']
        self.MINIKUBE_DIR = config_files['lwh_dir'] + "/minikube_offline"
        super().__init__()

    def status(self):
        # see if the kubectl command is installed ($(which kubectl)
        # get pods to see if we have the kube-system up
        if not os.path.isfile(self.KUBECTL):
            return NotInstalled

        log.info("running get pods")
        result = self.run(self.KUBECTL + ' get pods --namespace kube-system | grep Running', shell=True)

        if len(result.stdout.splitlines()) == 9:  # should we just say >0?
            return Running
        else:
            return NotRunning

    def install(self):
        # install the app
        if self.status() != NotInstalled:
            raise Exception('minikube is already installed')

        with pushd(self.MINIKUBE_DIR):
            cmd = self.MINIKUBE_DIR + '/minikube-offline_install.sh'
            result = self.run(cmd, shell=True, cwd=self.MINIKUBE_DIR, timeout=5*60)
            # we should log this or something
            return result

    def start(self):
        # start the app
        # minikube is started automatically by docker.
        # we should never have to start it
        return True
        # if we do have to, this is how:
        # if self.status() == Running:
        #    raise Exception('minikube is already running')
        #   minikube start --driver=none --apiserver-port=6443 --extra-config=kubelet.housekeeping-interval=10s --kubernetes-version v1.23.1
        #   minikube addons enable ingress --images="IngressController=ingress-nginx/controller:v1.1.0,KubeWebhookCertgenCreate=k8s.gcr.io/ingress-nginx/kube-webhook-certgen:v1.1.1,KubeWebhookCertgenPatch=k8s.gcr.io/ingress-nginx/kube-webhook-certgen:v1.1.1"
        #   minikube addons enable ingress-dns --images="IngressDNS=k8s-minikube/minikube-ingress-dns:0.0.2"
        #   minikube addons enable metrics-server --images="MetricsServer=metrics-server/metrics-server:v0.4.2"
        #   minikube addons enable dashboard --images="Dashboard=kubernetesui/dashboard:v2.3.1,MetricsScraper=kubernetesui/metrics-scraper:v1.0.7"
        #   mkdir -p /opt/local-path-provisioner
        #   kubectl apply -f /opt/local-weka-home/minikube_offline/local-path-storage.yaml

    def stop(self):
        # stop the app
        if self.status() != Running:
            raise Exception('minikube is not running')

        cmd = [self.MINIKUBE, 'stop']
        self.run(cmd, timeout=60)
        return True


class LocalWekaHome(AppBase):
    # Local Weka Home class
    def __init__(self):
        config_files = st.session_state.app_config.app_config['config_files']

        self.CONFIG = config_files['lwh_config_file']
        self.HELM = '/usr/bin/helm'
        self.KUBECTL = '/usr/bin/kubectl'
        self.CHECK_UP = [self.KUBECTL, 'wait', '--for=condition=ready', 'pod', '-l', 'app.group=common', '-n',
                         'home-weka-io', '--timeout=5m']
        self.RM_KUBE_GRAFANA = [self.KUBECTL, 'delete', 'pod', '-n', 'home-weka-io', '-l',
                                'app.kubernetes.io/name=grafana']
        self.LWH_DIR = config_files['lwh_dir'] + '/wekahome_offline'
        tarball_list = glob.glob(self.LWH_DIR + '/home-weka-io-*.tgz')
        if len(tarball_list) == 0:
            raise Exception(f'ERROR: File not found: {self.LWH_DIR}/home-weka-io-*.tgz')
        elif len(tarball_list) != 1:
            raise Exception(f'ERROR: Too many files found: {tarball_list}')
        self.LWH_TARBALL = tarball_list[0]
        self.UPDATE = [self.HELM, 'upgrade', 'homewekaio', '--namespace', 'home-weka-io', self.LWH_TARBALL,
                       '--create-namespace', '-f', self.CONFIG, '--debug']

        split_filename = self.LWH_TARBALL.split('/')
        filename = split_filename[-1][:-4]  # trim off '.tgz'
        self.version = filename.split('-')[-1]
        # We'll make minikube a sub-part of LWH...
        self.minikube = MiniKube()
        super().__init__()

    def status(self):
        # returns status of the app (NotInstalled, NotRunning, Running)
        if not os.path.isfile(self.CONFIG):
            return NotInstalled

        # if minikube isn't installed, LWH certainly isn't
        minikube_status = self.minikube.status()
        if minikube_status != Running:
            return minikube_status  # NotRunning or NotInstalled

        cmd = [self.KUBECTL, 'get', 'pods', '--namespace', 'home-weka-io']
        result = self.run(cmd, timeout=15)

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

        if self.minikube.status() == NotInstalled:
            try:
                self.minikube.install()
            except Exception as exc:
                raise Exception(f'Minikube install failed: {exc}')

        with pushd(self.LWH_DIR):
            # so we've already asked if LWH is installed, so we can assume this file isn't there
            # shutil.copyfile(self.CUSTOMER_CONFIG_FILE, self.CONFIG)
            # run the install script
            cmd = self.LWH_DIR + '/wekahome-install.sh'
            result = self.run(cmd, timeout=7 * 60, shell=True)
            if result.returncode != 0:
                log.debug(result.stdout)
                log.debug(result.stderr)
                raise Exception(f"Errors installing LWH")
            return True

    def start(self):
        # start the app

        try:
            self.run(self.UPDATE, timeout=90)
        except Exception as exc:
            raise Exception(f'Local Weka Home update failed {exc}')

        # remove grafana?
        self.run(self.RM_KUBE_GRAFANA, timeout=30)

        self.run(self.CHECK_UP, timeout=30)

        return True

    def stop(self):
        # stop the app
        pass

    def admin_password(self):
        str_cmd = self.KUBECTL + \
                  " get secret -n home-weka-io weka-home-admin-credentials  -o jsonpath='{.data.admin_password}'"
        result = self.run(str_cmd, shell=True)

        password = base64.b64decode(result.stdout)
        return password.decode('utf-8')

    def grafana_password(self):
        str_cmd = "kubectl get secret -n home-weka-io weka-home-grafana-credentials  -o jsonpath='{.data.password}'"

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
            result = self.run(cmd, shell=True)
        except CalledProcessError:
            return NotInstalled     # grep will return 1 if no matches
        log.debug(result)

        # make sure there are 3 wekasolutions containers (export, quota-export, and snaptool)
        if len(result.stdout.splitlines()) != 3:
            return NotInstalled

        with pushd(self.WEKAMON_DIR):
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
        with pushd(self.WEKAMON_DIR):
            log.info("running install.sh")
            cmd = './install.sh'
            result = run(cmd, shell=True)
            log.info(result)

            log.info("running docker load")
            cmd = ['/usr/bin/docker', 'load', '-i', 'wekamon-containers.tar.gz']
            result = self.run(cmd, timeout=30)
            log.info(result)

    def start(self):
        # start the app
        with pushd(self.WEKAMON_DIR):
            log.info("running docker compose up")
            cmd = ['/usr/bin/docker', 'compose', 'up', '-d']
            result = self.run(cmd, timeout=20)
            log.debug(result)

    def stop(self):
        # stop the app
        with pushd(self.WEKAMON_DIR):
            log.info("running docker compose down")
            cmd = ['/usr/bin/docker', 'compose', 'down']
            result = self.run(cmd, timeout=10)
            log.debug(result)

    def run(self, cmd, *args, capture_output=True, check=True, text=True, timeout=5, **kwargs):
        # print(f'WEKAmon: Running {cmd}: {kwargs}')
        if 'cwd' not in kwargs:
            kwargs['cwd'] = self.WEKAMON_DIR
        return super().run(cmd, *args, capture_output=capture_output, check=check, text=text, timeout=timeout, **kwargs)
        # print(result)
        # return result

