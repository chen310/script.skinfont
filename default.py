# -*- coding: utf-8 -*-
# main import's 
import sys, os
import xbmc, xbmcaddon, xbmcgui, xbmcvfs
from xml.dom import minidom

# Script constants 
__addon__     = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__cwd__       = xbmcvfs.translatePath(__addon__.getAddonInfo('path'))
__profile__   = xbmcvfs.translatePath(__addon__.getAddonInfo('profile'))
__language__  = __addon__.getLocalizedString

# Shared resources
BASE_RESOURCE_PATH = os.path.join(__cwd__, 'resources', 'lib')
sys.path.append (BASE_RESOURCE_PATH)

def fixed_writexml(self, writer, indent="", addindent="", newl=""):
    # indent = current indentation
    # addindent = indentation to add to higher levels
    # newl = newline string
    writer.write(indent+"<" + self.tagName)

    attrs = self._get_attributes()
    a_names = attrs.keys()

    for a_name in a_names:
        writer.write(" %s=\"" % a_name)
        minidom._write_data(writer, attrs[a_name].value)
        writer.write("\"")
    if self.childNodes:
        if len(self.childNodes) == 1 \
          and self.childNodes[0].nodeType == minidom.Node.TEXT_NODE:
            writer.write(">")
            self.childNodes[0].writexml(writer, "", "", "")
            writer.write("</%s>%s" % (self.tagName, newl))
            return
        writer.write(">%s"%(newl))
        for node in self.childNodes:
            if node.nodeType is not minidom.Node.TEXT_NODE:
                node.writexml(writer,indent+addindent,addindent,newl)
        writer.write("%s</%s>%s" % (indent,self.tagName,newl))
    else:
        writer.write("/>%s"%(newl))
# replace minidom's function with ours
minidom.Element.writexml = fixed_writexml

def getres(addonid):
    filepath = os.path.join(addonspath, addonid, 'addon.xml')
    doc = minidom.parse(filepath)
    root = doc.documentElement
    items = root.getElementsByTagName('extension')
    for item in items:
        point = item.getAttribute('point')
        if point == 'xbmc.gui.skin':
            ress = item.getElementsByTagName('res')
            list = []
            for res in ress:
                if res.getAttribute('folder') not in list:
                    list.append(res.getAttribute('folder'))
            return list
    return []

def addfont(addonid, folder):
    fonts_path = os.path.join(__profile__, 'fonts')
    font_list = ['arial.ttf']
    if os.path.exists(fonts_path):
        for f in os.listdir(fonts_path):
            if os.path.isfile(os.path.join(fonts_path, f)) and f.endswith('.ttf'):
                font_list.append(f)
    font_list.append('[COLOR red]选择本地字体文件[/COLOR]')
    sel = xbmcgui.Dialog().select('请选择要使用的字体文件', font_list)
    src = ''
    if sel < 0:
        return
    elif sel == 0:
        font_name = 'arial'
    elif sel == len(font_list) - 1:
        src = xbmcgui.Dialog().browseSingle(1, '选择字体文件', 'files', '.ttf', False, False)
        if not src:
            return
        font_name = os.path.basename(src)[:-4]
    else:
        src = os.path.join(fonts_path, font_list[sel])
        font_name = font_list[sel][:-4]
    if sel > 0:
        dst_path = os.path.join(os.path.dirname(
            os.path.dirname(__cwd__)), addonid, 'fonts')
        dst = os.path.join(dst_path, font_name + '.ttf')
        if not os.path.exists(dst_path):
            xbmcgui.Dialog().notification('字体复制出错', '字体文件夹不存在', xbmcgui.NOTIFICATION_INFO, 1000, False)
            return

        if not os.path.exists(dst) and not xbmcvfs.copy(src, dst):
            xbmcgui.Dialog().notification('字体复制出错', '复制失败', xbmcgui.NOTIFICATION_INFO, 1000, False)
            return

        if not os.path.exists(fonts_path):
            xbmcvfs.mkdir(fonts_path)
        if os.path.exists(fonts_path):
            xbmcvfs.copy(src, os.path.join(fonts_path, font_name + '.ttf'))

    filepath = os.path.join(addonspath, addonid, folder, 'Font.xml')
    doc = minidom.parse(filepath)
    root = doc.documentElement
    fontsets = root.getElementsByTagName('fontset')
    list = []
    font_pos = None
    for i in range(0,len(fontsets)):
        id = fontsets[i].getAttribute('id')
        if id.lower() == font_name.lower():
            ret = xbmcgui.Dialog().yesno('Skin Font',  font_name + '皮肤字体已存在。要重新生成Arial字体吗？', '否', '是')
            if not ret:
                return
            font_pos = i
        list.append(id)
    sel = xbmcgui.Dialog().select('请选择参照字体(%s)' % (folder), list)
    if sel < 0:
        return
    font_node = fontsets[sel].cloneNode(True)
    if font_pos:
        font_node.setAttribute("id", fontsets[font_pos].getAttribute("id"))
        root.removeChild(fontsets[font_pos])
        del fontsets[font_pos]
    else:
        font_node.setAttribute("id", font_name)
    if font_node.getAttribute("idloc") and sel != font_pos:
        font_node.removeAttribute("idloc")
    for node in font_node.getElementsByTagName("filename"):
        newText = doc.createTextNode(font_name + '.ttf')
        node.replaceChild(newText, node.firstChild)
    root.appendChild(font_node)
    with open(filepath, 'w', encoding='utf-8') as f:
        doc.writexml(f, addindent="    ", newl="\n")
    xbmcgui.Dialog().notification(addonid, font_name + '皮肤字体已生成', xbmcgui.NOTIFICATION_INFO, 1000, False)
addonspath = os.path.dirname(os.path.dirname(__cwd__))

addonlist = []
for addonid in os.listdir(addonspath):
    if os.path.isdir(os.path.join(addonspath, addonid)) and addonid[:4] == 'skin':
        addon = xbmcaddon.Addon(id=addonid)
        addonname = addon.getAddonInfo('name')
        addonlist.append((addonid, addonname))

list = [x[1] for x in addonlist]
if not list:
    xbmcgui.Dialog().ok('Skin Font', '未找到可用皮肤！')
else:
    sel = xbmcgui.Dialog().select('请选择要增加字体的皮肤', list)
    if sel != -1:
        addonid = addonlist[sel][0]
        for folder in getres(addonid):
            addfont(addonid, folder)