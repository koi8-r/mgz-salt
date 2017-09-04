import re, itertools


'''
HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall
HKLM\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall
HKLM\Software\Classes\Installer\Products
HKU\<SID>\Software\Microsoft\Windows\CurrentVersion\Uninstall
HKU\<SID>\Software\Microsoft\Installer\Products
HKLM\Software\Microsoft\Windows\CurrentVersion\Installer\UserData\<SID>\Products
Values:
 - SystemComponent
 - WindowsInstaller
 - UninstallString
 - ReleaseType
 - ParentKeyName
'''

installer_reg_path_0 = ('HKLM', 'Software\\Classes\\Installer\\Products',)
uninstaller_reg_path = ('HKLM', 'Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall',)
installer_reg_path_1 = ('HKLM', 'Software\\Microsoft\\Windows\\CurrentVersion\\Installer\\UserData\\S-1-5-18\\Products',)


# todo: backreference
product_guid_regex = re.compile(r'(?iu)^\{([A-Z0-9]{8})-([A-Z0-9]{4})-([A-Z0-9]{4})-([A-Z0-9]{4})-([A-Z0-9]{12})\}$')
product_code_regex = re.compile(r'(?iu)^[A-Z0-9]{32}$')


def guid2guid(_):
    return _ if _ and product_guid_regex.match(_) else None


def code2code(_):
    return _ if _ and product_code_regex.match(_) else None


def guid2code(guid):
    """Convert MSI Installer product guid to product code"""
    if not guid:
        return None

    # todo: back reference
    _r = product_guid_regex.match(guid)
    if _r:
        return unicode(reduce(lambda a, _: a + _,
                              itertools.chain(
                                  reversed(_r.group(1)),
                                  reversed(_r.group(2)),
                                  reversed(_r.group(3)),
                                  reversed(_r.group(4)[:2]),
                                  reversed(_r.group(4)[2:]),
                                  reversed(_r.group(5)[:2]),
                                  reversed(_r.group(5)[2:4]),
                                  reversed(_r.group(5)[4:6]),
                                  reversed(_r.group(5)[6:8]),
                                  reversed(_r.group(5)[8:10]),
                                  reversed(_r.group(5)[10:12]),
                              ),
                              ''))
    else:
        return None


def code2guid(code):
    """convert MSI Installer product code to product guid"""
    if not code:
        return None

    _r = product_code_regex.match(code)

    if _r:
        return unicode('{' +
                       ''.join(reversed(code[:8])) + '-' +
                       ''.join(reversed(code[8:12])) + '-' +
                       ''.join(reversed(code[12:16])) + '-' +
                       ''.join(reversed(code[16:18])) +
                       ''.join(reversed(code[18:20])) + '-' +
                       ''.join(reversed(code[20:22])) +
                       ''.join(reversed(code[22:24])) +
                       ''.join(reversed(code[24:26])) +
                       ''.join(reversed(code[26:28])) +
                       ''.join(reversed(code[28:30])) +
                       ''.join(reversed(code[30:32])) +
                       '}')
    else:
        return None
