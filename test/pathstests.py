"""Directory generation and installroot tests."""

from testbase import *

import shutil
import subprocess
import tempfile
import types
from distutils.spawn import find_executable


SOURCE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(SOURCE, 'rpmUtils', 'paths.py.in')
CONFIG = os.path.join(SOURCE, 'Config.mak')


class PathsTests(unittest.TestCase):
    def setUp(self):
        self.workdir = tempfile.mkdtemp(prefix='yum-paths-')
        package = os.path.join(self.workdir, 'rpmUtils')
        os.mkdir(package)
        shutil.copy(TEMPLATE, package)
        shutil.copy(CONFIG, self.workdir)
        with open(os.path.join(self.workdir, 'Makefile'), 'w') as makefile:
            makefile.write('include Config.mak\nall: $(PATHSPY)\n')
        self.output = os.path.join(package, 'paths.py')

    def tearDown(self):
        shutil.rmtree(self.workdir)

    def generate(self, root='/', prefix='/usr', conf='/etc', state='/var'):
        subprocess.check_call(['make', '-s', '-C', self.workdir, 'all',
                               'ROOTPREFIX=' + root, 'PREFIX=' + prefix,
                               'SYSCONFDIR=' + conf, 'LOCALSTATEDIR=' + state])
        return self.load(self.output)

    def load(self, filename):
        module = types.ModuleType('configured_paths')
        with open(filename) as source:
            code = compile(source.read(), filename, 'exec')
        eval(code, module.__dict__)
        return module

    def test_unix_and_alternate_root(self):
        paths = self.generate()
        conf = FakeConf()
        self.assertEqual(paths.rooted(conf.installroot, '/var/cache/yum'),
                         '/var/cache/yum')
        conf.installroot = '/stage'
        self.assertEqual(paths.rooted(conf.installroot, '/etc/yum/yum.conf'),
                         '/stage/etc/yum/yum.conf')
        self.assertEqual(paths.rooted(conf.installroot,
                                      '/stage/var/cache/yum'),
                         '/stage/var/cache/yum')
        self.assertEqual(paths.rooted('/tmp/user-cache', 'yum.pid'),
                         '/tmp/user-cache/yum.pid')

    def test_leading_prefix_deduplication(self):
        paths = self.generate('/@unixroot', '/@unixroot/usr',
                              '/@unixroot/etc', '/@unixroot/var')
        self.assertEqual(paths.ROOTPREFIX, '/@unixroot/')
        self.assertEqual(paths.rooted(paths.ROOTPREFIX,
                                      '/@unixroot/var/cache/yum'),
                         '/@unixroot/var/cache/yum')
        self.assertEqual(paths.rooted(paths.ROOTPREFIX, '/@unixroot'),
                         '/@unixroot')
        self.assertEqual(paths.rooted(paths.ROOTPREFIX,
                                      '/@unixroot//var/./cache/yum'),
                         '/@unixroot/var/cache/yum')
        self.assertEqual(paths.rooted('/', '/@unixroot/@unixroot/var'),
                         '/@unixroot/@unixroot/var')

    def test_no_path_migration_or_alternate_root_rebasing(self):
        paths = self.generate('/@unixroot', '/@unixroot/usr',
                              '/@unixroot/etc', '/@unixroot/var')
        self.assertEqual(paths.rooted('/', '/var/cache/yum'), '/var/cache/yum')
        self.assertEqual(paths.rooted('/stage', '/var/cache/yum'),
                         '/stage/var/cache/yum')
        self.assertEqual(paths.rooted('/stage', '/@unixroot/var/cache/yum'),
                         '/stage/@unixroot/var/cache/yum')
        self.assertEqual(paths.rooted('C:/target', '/@unixroot/var/lib/rpm'),
                         'C:/target/@unixroot/var/lib/rpm')
        self.assertEqual(paths.rooted('C:/@unixroot', '/@unixroot/var/lib/rpm'),
                         'C:/@unixroot/@unixroot/var/lib/rpm')

    def test_no_special_treatment_for_configured_directories(self):
        paths = self.generate('/system', '/apps/yum', '/settings', '/state')
        for path in ('/apps/yum/share/yum-cli', '/settings/yum/yum.conf',
                     '/state/cache/yum'):
            self.assertEqual(paths.rooted('/system', path), '/system' + path)
            self.assertEqual(paths.rooted('/stage', path), '/stage' + path)
        self.assertEqual(paths.rooted('/system', '/system/lib/sendmail'),
                         '/system/lib/sendmail')
        self.assertEqual(paths.rooted('/stage', '/system/lib/sendmail'),
                         '/stage/system/lib/sendmail')

    def test_directory_boundaries(self):
        paths = self.generate('/system', '/apps', '/settings', '/state')
        self.assertEqual(paths.rooted('/system', '/systematic/file'),
                         '/system/systematic/file')
        self.assertEqual(paths.rooted('/', '/systematic/system/file'),
                         '/systematic/system/file')
        self.assertEqual(paths.rooted('/system', '/stateful/file'),
                         '/system/stateful/file')
        self.assertEqual(paths.rooted('/stage', '/stagecoach/file'),
                         '/stage/stagecoach/file')

    def test_regeneration_and_quoting(self):
        self.generate()
        os.utime(self.output, (1000000000, 1000000000))
        self.generate()
        unchanged = os.path.getmtime(self.output)
        varsfile = os.path.join(self.workdir, 'paths.vars')
        varsmtime = os.path.getmtime(varsfile)
        self.generate()
        self.assertEqual(os.path.getmtime(self.output), unchanged)
        self.assertEqual(os.path.getmtime(varsfile), varsmtime)
        paths = self.generate(prefix='/apps/yum', conf='/settings/')
        self.assertEqual(paths.PREFIX, '/apps/yum')
        self.assertEqual(paths.SYSCONFDIR, '/settings/')
        with open(varsfile) as source:
            self.assertEqual(source.read().strip(),
                             'ROOTPREFIX=/ PREFIX=/apps/yum '
                             'SYSCONFDIR=/settings/ LOCALSTATEDIR=/var')

    def test_make_install_generates_and_installs_paths(self):
        package = os.path.join(self.workdir, 'rpmUtils')
        for name in ('Makefile', '__init__.py'):
            shutil.copy(os.path.join(SOURCE, 'rpmUtils', name), package)
        staging = os.path.join(self.workdir, 'staging')
        command = ['make', '-s', '-C', package, 'install',
                   'PYTHON=' + sys.executable, 'PYVER=2.7', 'PYSYSDIR=/python',
                   'INSTALL=' + find_executable('install'),
                   'MKDIR=' + find_executable('mkdir'),
                   'ROOTPREFIX=/system', 'PREFIX=/apps', 'SYSCONFDIR=/settings',
                   'LOCALSTATEDIR=/state', 'DESTDIR=' + staging]
        env = os.environ.copy()
        env['PYTHONPYCACHEPREFIX'] = os.path.join(self.workdir, 'bytecode')
        subprocess.check_output(command, env=env)
        installed = os.path.join(staging, 'python/lib/python2.7/site-packages',
                                 'rpmUtils/paths.py')
        paths = self.load(installed)
        self.assertEqual((paths.ROOTPREFIX, paths.PREFIX, paths.SYSCONFDIR,
                          paths.LOCALSTATEDIR),
                         ('/system/', '/apps', '/settings', '/state'))
        with open(installed) as source:
            self.assertNotIn(staging, source.read())
        # A second make with different values must update installed output too.
        command[command.index('SYSCONFDIR=/settings')] = 'SYSCONFDIR=/new-settings'
        subprocess.check_output(command, env=env)
        self.assertEqual(self.load(installed).SYSCONFDIR, '/new-settings')

    def test_recursive_make_propagates_directories(self):
        os.mkdir(os.path.join(self.workdir, 'yum'))
        shutil.copy(os.path.join(SOURCE, 'yum', 'Makefile'),
                    os.path.join(self.workdir, 'yum', 'Makefile'))
        variables = ['PYTHON=' + sys.executable, 'ROOTPREFIX=/system',
                     'PREFIX=/apps', 'SYSCONFDIR=/settings', 'LOCALSTATEDIR=/state']
        subprocess.check_output(['make', '-s', '-C', self.workdir, 'all'] + variables)
        output = os.path.join(self.workdir, 'rpmUtils', 'paths.py')
        paths = self.load(output)
        self.assertEqual((paths.ROOTPREFIX, paths.PREFIX, paths.SYSCONFDIR,
                          paths.LOCALSTATEDIR),
                         ('/system/', '/apps', '/settings', '/state'))
        variables[variables.index('PREFIX=/apps')] = 'PREFIX=/other-apps'
        subprocess.check_output(['make', '-s', '-C',
                                 os.path.join(self.workdir, 'yum')] + variables)
        with open(os.path.join(self.workdir, 'paths.vars')) as source:
            self.assertIn('PREFIX=/other-apps', source.read())
        self.assertEqual(self.load(output).PREFIX, '/other-apps')


if __name__ == '__main__':
    unittest.main()
