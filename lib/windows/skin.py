# -*- coding: utf-8 -*-
import os
import xbmc
import xbmcvfs
from lib import util

# Skins that work without font modification:
#
# skin.aeon.nox.5
# skin.xperience1080
# skin.mimic
# skin.neon <- No font30, but I'll leave it for now
# skin.bello

FONT_TRANSLATIONS = {
    'skin.maximinimalism': {'font10': 'smallMedium',            'font13': 'regular',         'font30': 'large'},
    'skin.back-row':       {'font10': 'font12',                 'font13': 'special14',       'font30': 'special16'},
    'skin.box':            {'font10': 'Panel_ItemChooser',      'font13': 'List_Focused',    'font30': 'Panel_Description_Title'},
    'skin.titan':          {'font10': 'Reg24',                  'font13': 'font13',          'font30': 'Reg42'},
    'skin.rapier':         {'font10': 'ListFont5',              'font13': 'WeatherCurrentReadingFont2', 'font30': 'FullMediaInfoTitleFont3'},
    'skin.sio2':           {'font10': 'size22',                 'font13': 'size28',          'font30': 'size38'},
    'skin.blackglassnova': {'font10': 'rss',                    'font13': 'SmallButtonFont', 'font30': 'WindowTitleFont'},
    'skin.nebula':         {'font10': 'BadgeFont',              'font13': 'SmallButtonFont', 'font30': 'InfoTitleFont'},
    'skin.transparency':   {'font10': 'font-15',                'font13': 'font13',          'font30': 'font-30'},
    'skin.arctic.zephyr':  {'font10': 'Mini',                   'font13': 'font13',          'font30': 'Large'},
    'skin.apptv':          {'font10': 'font10',                 'font13': 'font10',          'font30': 'font18'},  # No font10 equivalent
    'skin.eminence':       {'font10': 'Font-RSS',               'font13': 'font13',          'font30': 'Font-ViewCategory'},
    'skin.amber':          {'font10': 'GridItems',              'font13': 'Details',         'font30': 'MainLabelBigTitle'},  # Old gui API level
    'skin.metropolis':     {'font10': 'METF_DialogVerySmall',   'font13': 'font13',          'font30': 'METF_TitleTextLarge'},
    'skin.quartz':         {'font10': 'size14',                 'font13': 'font13',          'font30': 'size28'}  # Old gui API level - alignment flaws
}

# helix skins to check =  [' skin.refocus', ' skin.1080xf', ' skin.conq']

FONTS = ('font10', 'font13', 'font30')

VERSION = util.ADDON.getAddonInfo('version')
VERSION_FILE = os.path.join(xbmcvfs.translatePath(util.ADDON.getAddonInfo('profile')), 'skin', 'version')


def skinningAPIisOld():
    try:
        return util.Version(util.xbmcaddon.Addon('xbmc.gui').getAddonInfo('version')) < util.Version('5.2.0')
    except:
        util.ERROR()
        return False

OLD_API = skinningAPIisOld()


LIVETV = 'script-tablo-livetv.xml'


SKINS_XMLS = (LIVETV,)


def copyTree(source, target):
    pct = 0
    mod = 5
    if not source or not target:
        return
    if not os.path.isdir(source):
        return
    sourcelen = len(source)
    if not source.endswith(os.path.sep):
        sourcelen += 1
    for path, dirs, files in os.walk(source):  # @UnusedVariable
        subpath = path[sourcelen:]
        xbmcvfs.mkdir(os.path.join(target, subpath))
        for f in files:
            xbmcvfs.copy(os.path.join(path, f), os.path.join(target, subpath, f))
            pct += mod
            if pct > 100:
                pct = 95
                mod = -5
            elif pct < 0:
                pct = 5
                mod = 5


def currentKodiSkin():
    skinPath = xbmcvfs.translatePath('special://skin').rstrip('/\\')
    return os.path.basename(skinPath)


def setupDynamicSkin():
    import shutil
    targetDir = os.path.join(xbmcvfs.translatePath(util.ADDON.getAddonInfo('profile')), 'skin', 'resources')
    target = os.path.join(targetDir, 'skins')

    if os.path.exists(target):
        shutil.rmtree(target, True)
    if not os.path.exists(targetDir):
        os.makedirs(targetDir)

    source = os.path.join(xbmcvfs.translatePath(util.ADDON.getAddonInfo('path')), 'resources', 'skins')
    copyTree(source, target)


def customizeSkinXML(skin, xml):
    source = os.path.join(xbmcvfs.translatePath(util.ADDON.getAddonInfo('path')), 'resources', 'skins', 'Main', '720p', xml)
    target = os.path.join(xbmcvfs.translatePath(util.ADDON.getAddonInfo('profile')), 'skin', 'resources', 'skins', 'Main', '720p', xml)
    with open(source, 'r') as s:
        data = s.read()

    for font in FONTS:
        data = data.replace(font, '@{0}@'.format(font))
    for font in FONTS:
        data = data.replace('@{0}@'.format(font), FONT_TRANSLATIONS[skin][font])

    with open(target, 'w') as t:
        t.write(data)


def updateNeeded():
    if not os.path.exists(VERSION_FILE):
        return True
    with open(VERSION_FILE, 'r') as f:
        version = f.read()
    if version != '{0}:{1}:{2}'.format(currentKodiSkin(), VERSION, OLD_API and ':old' or ''):
        return True
    return False


def init():
    if updateNeeded():
        try:
            setupDynamicSkin()
        except:
            util.ERROR()

    return os.path.join(xbmcvfs.translatePath(util.ADDON.getAddonInfo('profile')), 'skin')


def getSkinPath():
    skin = currentKodiSkin()
    default = util.ADDON.getAddonInfo('path')
    if skin == 'skin.confluence':
        return default
    if skin not in FONT_TRANSLATIONS:
        return default
    if updateNeeded():
        util.DEBUG_LOG('Updating custom skin')
        try:
            setupDynamicSkin()

            for xml in SKINS_XMLS:
                customizeSkinXML(skin, xml)
            with open(VERSION_FILE, 'w') as f:
                f.write('{0}:{1}:{2}'.format(currentKodiSkin(), VERSION, OLD_API and ':old' or ''))
        except:
            util.ERROR()
            return default

    util.DEBUG_LOG('Using custom fonts for: {0}'.format(skin))

    return os.path.join(xbmcvfs.translatePath(util.ADDON.getAddonInfo('profile')), 'skin')
