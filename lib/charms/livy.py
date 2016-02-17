from glob import glob
from path import Path
from subprocess import CalledProcessError

import jujuresources
from charmhelpers.core import hookenv
from charmhelpers.core import host
from charmhelpers.core import unitdata
from charmhelpers.fetch.archiveurl import ArchiveUrlFetchHandler
from jujubigdata import utils


# Main Livy class for callbacks
class Livy(object):
    def __init__(self, dist_config):
        self.dist_config = dist_config
        self.resources = {
            'livy': 'livy-%s' % utils.cpu_arch(),
        }
      self.verify_resources = utils.verify_resources(*self.resources.values())

    def install(self):
        default_conf = self.dist_config.path('livy') / 'conf'
        livy_conf = self.dist_config.path('livy_conf')
        livy_conf.rmtree_p()
        default_conf.copytree(livy_conf)
          livy_bin = self.dist_config.path('livy') / 'bin'
          with utils.environment_edit_in_place('/etc/environment') as env:
            if livy_bin not in env['PATH']:
                env['PATH'] = ':'.join([env['PATH'], livy_bin])
            hadoop_cp = '/etc/hadoop/conf:/usr/lib/hadoop/share/hadoop/common/lib/*:/usr/lib/hadoop/share/hadoop/common/*\
:/usr/lib/hadoop/share/hadoop/hdfs:/usr/lib/hadoop/share/hadoop/hdfs/lib/*\
:/usr/lib/hadoop/share/hadoop/hdfs/*:/usr/lib/hadoop/share/hadoop/yarn/lib/*\
:/usr/lib/hadoop/share/hadoop/yarn/*:/usr/lib/hadoop/share/hadoop/mapreduce/lib/*\
:/usr/lib/hadoop/share/hadoop/mapreduce/*:/usr/lib/hadoop/contrib/capacity-scheduler/*.jar'
            env['CLASSPATH'] = hadoop_cp

        cmd = "chown -R hue:hadoop {}".format(self.dist_config.path('livy'))
        call(cmd.split())
        cmd = "chown -R hue:hadoop {}".format(self.dist_config.path('livy_conf'))
        call(cmd.split())

    def start(self):
        if not utils.jps("Main"):
            livy_log = self.dist_config.path('livy_logs') + 'livy-server.log'
            livy_home = self.dist_config.path('livy')
            # chdir here because things like zepp tutorial think ZEPPELIN_HOME
            # is wherever the daemon was started from.
            os.chdir(livy_home)
            utils.run_as('hue', './bin/livy-server', '2>&1', livy_log, '&' )

    def stop(self):
        livy_conf = self.dist_config.path('livy_conf')
        livy_home = self.dist_config.path('livy')
        utils.run_as('hue', 'pkill', '-9', '-u', 'hue')

    def open_ports(self):
        for port in self.dist_config.exposed_ports('livy'):
            hookenv.open_port(port)

    def close_ports(self):
        for port in self.dist_config.exposed_ports('livy'):
            hookenv.close_port(port)

