# coding=utf-8
import logging
from fnmatch import fnmatch
from pkg_util import code2guid, guid2code, code2code, guid2guid
from salt.utils import is_windows


log = logging.getLogger(__name__)
__virtualname__ = 'mgz_pkg'


def __virtual__():
    if is_windows():
        return __virtualname__
    return False, "Module mgz: module only works on Windows systems",


installer_reg_path_0 = ('HKLM', r'Software\Classes\Installer\Products',)
installer_reg_path_1 = ('HKLM', r'Software\Microsoft\Windows\CurrentVersion\Installer\UserData\{}\Products',)
installer_reg_path_2 = ('HKU', r'{}\Software\Microsoft\Windows\CurrentVersion\Uninstall',)
installer_reg_path_3 = ('HKU', r'{}\Software\Microsoft\Installer\Products',)
uninstall_reg_path_0 = ('HKLM', r'Software\Microsoft\Windows\CurrentVersion\Uninstall',)
uninstall_reg_path_1 = ('HKLM', r'Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall',)


def msword2007_compat():
    if search(b'Microsoft Office - профессиональный выпуск версии 2003'):
        return True if search(b'Пакет обеспечения совместимости для выпуска 2007 системы Microsoft Office') \
                else False
    else:
        return True


# TODO:
# compare pkg db after each uninstall
# report if nothing uninstalled
# separate by msi exe uninstall, registry uninstall string, winrepo uninstall command
# skip protected pkgs
def uninstall(name=None, _w=False):
    salt_ctx = globals()['__salt__']
    salt_run_all = salt_ctx['cmd.run_all']

    cmd = ['msiexec.exe', '/qn', '/norestart', '/X']
    ret = {}

    for guid, pkg in search(name, _w).iteritems():
        pkg_name = pkg.get('ProductName') or pkg.get('DisplayName') or guid
        guid = guid2guid(guid)
        log.info('Remove pkg \'%s\' (%s)', pkg_name, guid)

        if guid:
            result = salt_run_all(cmd + [guid], output_loglevel='trace', python_shell=False, redirect_stderr=True)
            if not result['retcode']:
                ret[pkg_name] = {'status': 'success'}
                log.info('Success remove pkg \'%s\'', pkg_name)
            else:
                log.error('Failed remove pkg \'%s\'', pkg_name)
                ret[pkg_name] = {'comment': result['stdout']}
                ret[pkg_name] = {'status': 'failed'}
        else:
            log.error('No guid for pkg \'%s\'', pkg_name)
            ret[pkg_name] = {'comment': 'no guid'}
            ret[pkg_name] = {'uninstall status': 'failed'}

    ret['result'] = True if not search(name, _w) else False
    return ret


def search(name=None, _w=False):
    """
    :param name: optional - pkg name glob for filter
    :param _w:  optional, internal - if execute salt-call on windows machine
    :return:

    CLI Example:

    .. code-block:: bash

        salt '*' mgz_pkg.search "Skype*"
    """
    def filter_fn(vname):
        if not name:
            return lambda _: True
        else:
            _name = name.decode('utf-8' if not _w else 'mbcs').lower()
            return lambda _: type(_[1].get(vname)) is unicode and fnmatch(_[1].get(vname).lower(), _name)

    salt_ctx = globals()['__salt__']
    salt_get_repo_data = salt_ctx['pkg.get_repo_data']
    salt_refresh_repo_data = salt_ctx['pkg.refresh_db']
    salt_refresh_repo_data()
    repo_data = salt_get_repo_data()
    name_map = {k.decode('utf-8'):v for k,v in repo_data.get('name_map', {}).iteritems()}
    repo = repo_data.get('repo', {})

    res = {}

    for k, v in filter(filter_fn('ProductName'), _installer_iter()):
        guid = code2guid(k)
        res[guid.upper() if guid else k] = v

    for k, v in filter(filter_fn('DisplayName'), _uninstalls_iter()):
        guid = guid2guid(k)
        guid = guid.upper() if guid else k
        if res.get(guid):
            res[guid].update(v)
        else:
            res[guid] = v

        name = res[guid].get('DisplayName')
        ver = res[guid].get('DisplayVersion')
        res[guid].update({'salt_protect': res[guid].get('lan.mgz.salt:pkg:protect') is not None})
        res[guid].update({'salt_package': name_map.get(name)})
        res[guid].update({'salt_version': ver if ver and repo.get(res[guid].get('salt_package'), {}).get(ver) else None})

    return res


def installer():
    return dict(_installer_iter())


def uninstalls():
    return dict(_uninstalls_iter())


def _installer_iter():
    """
    :return: iter vkey: (vname:vdata)
    :rtype: tuple
    """
    """return tuple" reg_key:(vname:vdata)"""
    return (_ for _ in _keyvalues_iter(*(installer_reg_path_0 + ('ProductName', 'Version',))))


def _uninstalls_iter():
    """
    :return: iter vkey: (vname:vdata)
    :rtype: tuple
    """
    vnames = (
        'DisplayName',
        'DisplayVersion',
        'Version',
        'VersionMajor',
        'VersionMinor',
        'UninstallString',
        'QuietUninstallString',)

    return (_
            for reg_path in [uninstall_reg_path_0, uninstall_reg_path_1]  # Check 32 and 64 bit nodes
            for _ in _keyvalues_iter(*(reg_path + vnames))
            )


def _keyvalues_iter(hive, key, *names):
    salt_ctx = globals()['__salt__']
    salt_reg_list_keys = salt_ctx['reg.list_keys']
    salt_reg_read_value = salt_ctx['reg.read_value']

    return (
        (sub_key,
         dict(
             (vname, salt_reg_read_value(hive, ur'{0}\{1}'.format(key, sub_key), vname)['vdata'],)
             for vname in names
         ),)
        for sub_key in salt_reg_list_keys(hive, key)
    )
