import os
import shutil
import threading
import time
import zipfile
import webbrowser
import requests
from construct import *
from pathlib import Path

from kivy.clock import Clock, mainthread
from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.utils import platform

from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDIconButton, MDRoundFlatButton, MDRoundFlatIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.textfield import MDTextField


DISCORD_URL = "https://discord.gg/juZZs7hYwy"

GMA_VERSION = b"\x03".decode("utf-8")

BASE_OUTPUT_DIR = '/sdcard/Gmad_Extracted'
GMAD_OUTPUT_DIR = os.path.join(BASE_OUTPUT_DIR, 'GMAD_Files')
VPK_OUTPUT_DIR = os.path.join(BASE_OUTPUT_DIR, 'VPK_Files')

GMAFile = "all_file_meta" / Struct(
    "file_number" / Int32ul,
    "data"
    / IfThenElse(
        this.file_number != 0,
        "data"
        / Struct(
            "file_name" / CString("utf8"), "file_size" / Int64sl, "file_crc" / Int32ul
        ),
        Pass,
    ),
)


class FileContents(Adapter):
    def _encode(self, obj, context, path):
        return b"".join(obj)

    def _decode(self, obj, context, path):
        contents = []
        begin = 0
        for filemeta in context._.all_file_meta:
            if filemeta.file_number == 0:
                break

            size = filemeta.data.file_size
            contents.append(obj[begin: begin + size])
            begin += size

        return contents


def file_content_size(context):
    total = 0
    for filemeta in context.all_file_meta:
        if filemeta.file_number == 0:
            return total
        total += filemeta.data.file_size


GMAContents = "content" / Struct(
    "signature" / Const(b"GMAD"),
    "format_version" / PaddedString(1, "utf8"),
    "steamid" / Int64sl,
    "timestamp" / Int64sl,
    "required_content" / CString("utf8"),
    "addon_name" / CString("utf8"),
    "addon_description" / CString("utf8"),
    "addon_author" / CString("utf8"),
    "addon_version" / Int32sl,
    "all_file_meta" / RepeatUntil(lambda x, lst, ctx: x["file_number"] == 0, GMAFile),
    "total_file_size" / Computed(lambda ctx: file_content_size(ctx)),
    "embedded_files"
    / LazyStruct("contents" / FileContents(Bytes(this._.total_file_size))),
)

GMAVerifiedContents = "GMAVerifiedContents" / Struct(
    GMAContents,
    "addon_crc" / Optional(Int32ul),
    "MagicValue" / Optional(Int8ul),
)


class SolidBackground(Widget):
    """Pitch-black background that always exactly fills its parent layout,
    regardless of screen size or aspect ratio (phone, tablet, foldable, etc.)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.pos_hint = {'x': 0, 'y': 0}
        with self.canvas.before:
            Color(0.02, 0.02, 0.02, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


def watermark_label(text):
    return MDLabel(
        text=text,
        pos_hint={'center_x': 0.5, 'center_y': 0.5},
        halign='center',
        font_style='H3',
        bold=True,
        theme_text_color='Custom',
        text_color=(1, 1, 1, 0.06),
    )


class _DividerLine(Widget):
    def __init__(self, **kwargs):
        super().__init__(size_hint_y=None, height='1dp', **kwargs)
        with self.canvas:
            Color(1, 1, 1, 0.25)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class OrDivider(MDBoxLayout):
    """A modern 'line — OR — line' divider between two alternative actions."""

    def __init__(self, **kwargs):
        super().__init__(
            orientation='horizontal', size_hint=(0.6, None), height='24dp', spacing='12dp', **kwargs
        )
        self.add_widget(_DividerLine())
        self.add_widget(MDLabel(
            text='OR', size_hint=(None, None), size=('34dp', '24dp'),
            halign='center', bold=True,
            theme_text_color='Custom', text_color=(1, 1, 1, 0.55),
        ))
        self.add_widget(_DividerLine())


def make_dialog_text_label(text, halign='left'):
    """A label that always sizes itself exactly to fit its own text, so
    custom dialogs never end up with dead space below short text or clipped,
    overflowing text when it's long."""
    label = MDLabel(text=text, halign=halign, size_hint_y=None)
    label.bind(width=lambda inst, value: setattr(inst, 'text_size', (value, None)))
    label.bind(texture_size=lambda inst, value: setattr(inst, 'height', value[1]))
    return label


def make_adaptive_box(*widgets, spacing='12dp'):
    """A vertical box that always sizes itself exactly to fit its children.
    Used as content_cls for every custom MDDialog, so the dialog itself
    always matches whatever text ends up inside it."""
    box = MDBoxLayout(orientation='vertical', spacing=spacing, size_hint_y=None)
    for widget in widgets:
        box.add_widget(widget)
    box.bind(minimum_height=box.setter('height'))
    return box


class MainApp(MDApp):
    def ensure_storage_permissions(self):
        """Ask for storage access as soon as the app starts. On Android 10
        and below this pops the normal READ/WRITE_EXTERNAL_STORAGE runtime
        dialog. On Android 11+ those two don't grant real access to the
        whole sdcard anymore, so if 'All files access' hasn't been granted
        yet, this drops the user straight into the system settings screen
        for it."""
        if platform != 'android':
            return

        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
            ])
        except Exception:
            pass

        try:
            from jnius import autoclass

            Environment = autoclass('android.os.Environment')
            if not Environment.isExternalStorageManager():
                Intent = autoclass('android.content.Intent')
                Settings = autoclass('android.provider.Settings')
                Uri = autoclass('android.net.Uri')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')

                intent = Intent()
                intent.setAction(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
                uri = Uri.fromParts('package', PythonActivity.mActivity.getPackageName(), None)
                intent.setData(uri)
                PythonActivity.mActivity.startActivity(intent)
        except Exception:
            pass

    def open_discord_link(self, *args):
        webbrowser.open(DISCORD_URL)

    def build(self):
        self.ensure_storage_permissions()

        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.accent_palette = "Orange"

        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.on_select,
            background_color_toolbar="brown",
            background_color_selection_button="brown",
            icon_color="brown",
        )

        # main screen (GMA extractor)
        self.layout = MDFloatLayout()
        self.layout.add_widget(SolidBackground())
        self.layout.add_widget(watermark_label("GMAD\nEXTRACTOR"))

        self.text_input = MDTextField(
            hint_text="Path To The .GMA File.",
            pos_hint={'center_x': 0.35, 'center_y': 0.80},
            mode='round',
            helper_text='Ex: /sdcard/yourfile.gma',
            helper_text_mode="on_focus",
            size=(600, 600), size_hint_min=(None, None), size_hint_max=(490, 490),
        )
        self.layout.add_widget(self.text_input)

        extract_button = MDRoundFlatIconButton(
            text='Extract', icon='archive-arrow-down-outline',
            pos_hint={'center_x': 0.80, 'center_y': 0.80},
            text_color='black', md_bg_color='white',
        )
        extract_button.bind(on_press=self.on_clickk)
        self.layout.add_widget(extract_button)

        self.or_label_main = OrDivider(pos_hint={'center_x': 0.5, 'center_y': 0.70})
        self.layout.add_widget(self.or_label_main)

        info_button = MDFlatButton(
            text='Info', pos_hint={'center_x': 0.93, 'center_y': 0.98},
            theme_text_color="Custom", text_color='white',
        )
        info_button.bind(on_press=self.notif_on)
        self.layout.add_widget(info_button)

        errors_button = MDFlatButton(
            text='Errors', pos_hint={'center_x': 0.10, 'center_y': 0.98},
            theme_text_color="Custom", text_color='white',
        )
        errors_button.bind(on_press=self.notiff_onn)
        self.layout.add_widget(errors_button)

        choose_files_button = MDRoundFlatIconButton(
            text='Choose From Files', icon='folder-open-outline',
            pos_hint={'center_x': 0.5, 'center_y': 0.60},
            text_color='black', size_hint=(.9, .01), md_bg_color='white',
        )
        choose_files_button.bind(on_release=self.show_file_manager)
        self.layout.add_widget(choose_files_button)

        self.label = MDLabel(size=(600, 600), size_hint_min=(None, None), size_hint_max=(1200, 1000))
        self.layout.add_widget(self.label)

        # --- Second screen (VPK extractor) ---
        self.layout2 = FloatLayout()
        self.layout2.add_widget(SolidBackground())
        self.layout2.add_widget(watermark_label("VPK\nEXTRACTOR"))

        self.button_second_to_main = MDIconButton(
            icon="arrow-left", pos_hint={'center_x': 0.90, 'center_y': 0.95},
            theme_text_color='Custom', text_color='black', md_bg_color='white',
            on_press=self.switch_to_main_layout,
        )
        self.layout2.add_widget(self.button_second_to_main)

        choose_files_button2 = MDRoundFlatIconButton(
            text='Choose From Files', icon='folder-open-outline',
            pos_hint={'center_x': 0.5, 'center_y': 0.20},
            text_color='black', size_hint=(.9, .01), md_bg_color='white',
        )
        choose_files_button2.bind(on_release=self.show_file_manager)
        self.layout2.add_widget(choose_files_button2)

        self.text_input2 = MDTextField(
            hint_text="Path To The .VPK File.",
            pos_hint={'center_x': 0.35, 'center_y': 0.80},
            mode='round',
            helper_text='Ex: /sdcard/yourfile.vpk',
            helper_text_mode="on_focus",
            size=(600, 600), size_hint_min=(None, None), size_hint_max=(480, 480),
        )
        self.layout2.add_widget(self.text_input2)

        self.button22 = MDRoundFlatIconButton(
            text='Extract', icon='archive-arrow-down-outline',
            pos_hint={'center_x': 0.80, 'center_y': 0.80},
            text_color='black', md_bg_color='white',
        )
        self.button22.bind(on_press=self.on_clickkkk)
        self.layout2.add_widget(self.button22)

        self.or_label_second = OrDivider(pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.layout2.add_widget(self.or_label_second)

        self.label22 = MDLabel(size=(600, 600), size_hint_min=(None, None), size_hint_max=(1200, 1000))
        self.layout2.add_widget(self.label22)

        #Screen manager
        self.screen_manager = ScreenManager()

        self.main_screen = Screen(name="main")
        self.second_screen = Screen(name="second")

        self.button_main_to_second = MDRoundFlatButton(
            text='Extract VPK Files', pos_hint={'center_x': 0.5, 'center_y': 0.10},
            text_color='black', size_hint=(.9, .01), md_bg_color='white',
            on_press=self.switch_to_second_layout,
        )

        self.main_screen.add_widget(self.layout)
        self.main_screen.add_widget(self.button_main_to_second)
        self.second_screen.add_widget(self.layout2)

        self.screen_manager.add_widget(self.main_screen)
        self.screen_manager.add_widget(self.second_screen)

        Clock.schedule_once(self.maybe_show_startup_dialog, 0.3)

        return self.screen_manager

    def notif_on(self, instance):
        dialog = MDDialog(
            title="GmadExtractor",
            text="Created by: boo271\n\n"
                 "How to use:\n"
                 "1. Grant the app file access permission.\n"
                 "2. Enter the correct path to your GMAD file.\n"
                 "3. Large files may take a while to compress \u2014 just wait for the "
                 "process to finish.",
            buttons=[
                MDFlatButton(text="Join Discord", on_release=self.open_discord_link),
                MDFlatButton(text="OK", on_release=lambda *a: dialog.dismiss()),
            ],
        )
        dialog.open()

    def notiff_onn(self, instance):
        dialog = MDDialog(
            title="Gmad Errors",
            text="- If you get a 'This is not a GMAD file' error, you're probably trying "
                 "to extract an LZMA or BIN file. Open it with ZArchiver to view its "
                 "contents, extract it, then rename it to .gma.\n"
                 "- Extracting VPK files, all files should be in the same directory, otherwise it will throw an error\n"
                 "For any other error, DM boo271 on Discord \u2014 see the Info to "
                 "join the server.",
        )
        dialog.open()

    def show_file_manager(self, instance):
        self.file_manager.show('/sdcard')

    def on_clickk(self, instance):
        value = self.text_input.text.strip()
        if not value:
            self.show_dialogg("Error", "Please enter a path to your GMA file, or choose one from Files.")
            return
        if not os.path.exists(value):
            self.show_dialogg("Error", f"File not found:\n{value}")
            return

        self.label.pos_hint = {'center_x': 0.60, 'center_y': 0.90}
        self.label.color = (1, 1, 1, 1)
        self.label.text = ""
        self.show_dialog()
        threading.Thread(target=self.on_button_press, args=(value,), daemon=True).start()

    def on_clickkk(self, instance):
        self.label.pos_hint = {'center_x': 0.60, 'center_y': 0.90}
        self.label.color = (1, 1, 1, 1)
        self.label.text = ""
        self.show_dialog22()
        threading.Thread(target=self.on_submit, args=(None,), daemon=True).start()

    def on_clickkkk(self, instance):
        value = self.text_input2.text.strip()
        if not value:
            self.show_dialogg("Error", "Please enter a path to your VPK file, or choose one from Files.")
            return
        if not os.path.exists(value):
            self.show_dialogg("Error", f"File not found:\n{value}")
            return

        self.label22.pos_hint = {'center_x': 0.60, 'center_y': 0.88}
        self.label22.color = (1, 1, 1, 1)
        self.label22.text = ""
        self.show_dialog()
        threading.Thread(target=self.extract_vpk, args=(value,), daemon=True).start()

    @mainthread
    def show_dialog(self):
        self.progress_label = make_dialog_text_label('Starting...', halign='center')
        content = make_adaptive_box(
            MDSpinner(size_hint=(None, None), size=(46, 46), active=True,
                      pos_hint={'center_x': 0.5}),
            self.progress_label,
        )
        self.dialog = MDDialog(
            title='Extracting...',
            type="custom",
            auto_dismiss=False,
            content_cls=content,
        )
        self.dialog.open()

    @mainthread
    def update_progress(self, phase, done, total):
        percent = int(done / total * 100) if total else 0
        if getattr(self, 'progress_label', None):
            self.progress_label.text = f"{phase} {done}/{total} ({percent}%)"

    @mainthread
    def show_dialog22(self):
        self.progress_label = make_dialog_text_label('Starting...', halign='center')
        content = make_adaptive_box(
            MDSpinner(size_hint=(None, None), size=(46, 46), active=True,
                      pos_hint={'center_x': 0.5}),
            self.progress_label,
        )
        self.dialog = MDDialog(
            title='Downloading...',
            type="custom",
            auto_dismiss=False,
            content_cls=content,
        )
        self.dialog.open()

    @mainthread
    def show_dialogg(self, title, text):
        self.dialog = MDDialog(title=title, text=text, auto_dismiss=True)
        self.dialog.open()

    @mainthread
    def dialog_dismisss(self):
        if getattr(self, 'dialog', None):
            self.dialog.dismiss()
        self.label.text = ""

    def on_select(self, path: str):
        self.exit_manager()
        toast(path)
        self.text_input.text = str(path)
        self.text_input2.text = str(path)

    def exit_manager(self, *args):
        self.file_manager.close()

    def _should_report(self, done, total):
        """Throttle progress updates by wall-clock time (not file count), so
        archives with lots of files don't get slowed down by constant
        cross-thread UI updates. Always reports the first and last item."""
        now = time.time()
        last = getattr(self, '_last_progress_ts', 0)
        if done == 1 or done >= total or now - last >= 0.15:
            self._last_progress_ts = now
            return True
        return False

    def zip_folder_with_progress(self, folder, zip_path, phase="Compressing"):
        file_list = []
        for root, _dirs, files in os.walk(folder):
            for name in files:
                file_list.append(os.path.join(root, name))
        total = len(file_list) or 1

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i, file_path in enumerate(file_list, 1):
                zf.write(file_path, os.path.relpath(file_path, folder))
                if self._should_report(i, total):
                    self.update_progress(phase, i, total)

    def _write_entries_to_zip(self, entries, total, zip_path, phase="Extracting"):
        """Writes (name, data) pairs straight into the output zip.

        This is the fast path: no intermediate folder on the SD card, so
        each file gets written to storage exactly once instead of being
        written out, then read back in to be zipped. compresslevel=1 trades
        a bit of zip size for a lot of speed, which is worth it since most
        game assets (vtf/vtx/mdl/wav etc.) are already compressed and don't
        shrink much anyway."""
        total = total or 1
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
            for i, (name, data) in enumerate(entries, 1):
                zf.writestr(name, data)
                if self._should_report(i, total):
                    self.update_progress(phase, i, total)

    def extract_vpk(self, valuee):
      
        woww = os.path.splitext(os.path.basename(valuee))[0] or "output"

        try:
            import vpk
        except ModuleNotFoundError:
            self.label22.color = (1, 0, 0, 1)
            self.label22.text = "Error: the 'vpk' package is not installed."
            self.dialog_dismisss()
            self.show_dialogg("Error", "The 'vpk' package is not installed.\nRun: pip install vpk")
            return

        try:
            Path(VPK_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        except Exception as fe:
            self.label22.color = (1, 0, 0, 1)
            self.label22.text = f"Error: {fe}"
            self.dialog_dismisss()
            self.show_dialogg("Error", f"Could not create folders:\n{fe}")
            return

        try:
            with vpk.open(valuee) as package:
                entry_names = list(package)
                total = len(entry_names) or 1

                def entries():
                    for entry_name in entry_names:
                        yield entry_name, package[entry_name].read()

                self._write_entries_to_zip(entries(), total, f'{VPK_OUTPUT_DIR}/{woww}.zip')

            self.dialog_dismisss()
            self.show_dialogg("Extracted!", f"Saved to {VPK_OUTPUT_DIR}")
        except ValueError as fe:
            self.label22.color = (1, 0, 0, 1)
            self.dialog_dismisss()
            self.show_dialogg("Error", f"This does not look like a valid VPK file.\n{fe}")
            return
        except FileNotFoundError as fe:
            self.dialog_dismisss()
            self.show_dialogg(
                "Error",
                f"A required file could not be found:\n{fe}\n\n"
                "If this is a multi-part VPK (e.g. pak01_dir.vpk), make sure the numbered "
                "pak01_000.vpk, pak01_001.vpk, etc. files are in the same folder as the "
                "_dir.vpk file you picked.",
            )
            return
        except Exception as fe:
            self.label22.text = str(fe)
            self.dialog_dismisss()

    def on_submit(self, instance):
        try:
            shutil.rmtree('/sdcard/lon')
            shutil.rmtree('/sdcard/extracted')
            os.remove('/sdcard/thefile.7z')
        except Exception:
            pass

        try:
            Path('/sdcard/lon').mkdir(parents=True, exist_ok=True)
            Path(GMAD_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
            Path('/sdcard/extracted').mkdir(parents=True, exist_ok=True)
        except Exception:
            self.label.color = (1, 0, 0, 1)
            self.label.text = "Error: Please grant file access permission."
            self.dialog_dismisss()
            self.show_dialogg("Error", "Please grant file access permission.")
            return

        try:
            import lzma
            sss = requests.post(
                'https://ytshorts.savetube.me/api/v1/steam-workshop-downloader',
                data={'url': self.text_inputt.text},
            )
            if sss.status_code == 200:
                woow = sss.json()
                de = woow['response']
                if de[0]['file_url'] == '':
                    self.label.color = (1, 0, 0, 1)
                    self.label.text = "This mod is not available."
                    return

                gh = de[0]['file_url']
                ghh = de[0]['title']
                jj = requests.get(gh)
                with open('/sdcard/thefile.7z', 'wb') as f:
                    f.write(jj.content)
                with lzma.open('/sdcard/thefile.7z') as f:
                    file_content = f.read()
                with open('/sdcard/lon/qqq.gma', 'wb') as g:
                    g.write(file_content)

                dirr = '/sdcard/lon/qqq.gma'
                if dirr.endswith('.gma'):
                    with open(dirr, "rb") as file:
                        gma = GMAVerifiedContents.parse_stream(file)
                        total = len(gma.content.all_file_meta) - 1
                        for i in range(0, total):
                            meta = gma.content.all_file_meta[i]
                            gma_file_name = meta.data.file_name
                            file_name = os.path.join('/sdcard/extracted', gma_file_name)
                            file_folder = os.path.dirname(file_name)
                            if not os.path.exists(file_folder):
                                os.makedirs(file_folder)
                            with open(file_name, "wb") as output:
                                output.write(gma.content.embedded_files.contents[i])
                            if self._should_report(i + 1, total or 1):
                                self.update_progress("Extracting", i + 1, total or 1)

                    self.zip_folder_with_progress('/sdcard/extracted', f'{GMAD_OUTPUT_DIR}/{ghh}.zip')
                    self.label.pos_hint = {'center_x': 0.57, 'center_y': 0.90}
                    self.dialog_dismisss()
                    self.show_dialogg("Extracted!", f"Saved to {GMAD_OUTPUT_DIR}")

                    os.remove('/sdcard/lon/qqq.gma')
                    os.remove('/sdcard/thefile.7z')

                    for root, dirs, files in os.walk('/sdcard/extracted', topdown=False):
                        for name in dirs:
                            shutil.rmtree(os.path.join(root, name))
                        for name in files:
                            os.remove(os.path.join(root, name))
                else:
                    self.label.color = (1, 0, 0, 1)
                    self.label.text = "Error: please check your connection, or the link may be invalid."
                    self.dialog_dismisss()
                    self.show_dialogg("Error", "Please check your connection, or the link may be invalid.")
                    return
        except requests.exceptions.ConnectionError:
            self.label.color = (1, 0, 0, 1)
            self.dialog_dismisss()
            self.show_dialogg("Error", "Please check your internet connection.")
            return
        except PermissionError:
            self.label.color = (1, 0, 0, 1)
            self.label.pos_hint = {'center_x': 0.57, 'center_y': 0.90}
            self.dialog_dismisss()
            self.show_dialogg("Error", "Failed. Please grant file access permission.")
            return
        except FileNotFoundError:
            self.label.pos_hint = {'center_x': 0.57, 'center_y': 0.90}
            self.label.color = (0, 1, 0, 1)
            self.dialog_dismisss()
            self.show_dialogg("Extracted!", f"Extraction succeeded! Saved to {GMAD_OUTPUT_DIR}.")
            for root, dirs, files in os.walk('/sdcard/extracted', topdown=False):
                for name in dirs:
                    shutil.rmtree(os.path.join(root, name))
                for name in files:
                    os.remove(os.path.join(root, name))
            return
        except Exception as Fr:
            self.label.text = str(Fr)
            self.dialog_dismisss()
            return

    def on_button_press(self, value: str):
        try:
            shutil.rmtree('/sdcard/lon')
            shutil.rmtree('/sdcard/extracted')
            os.remove('/sdcard/thefile.7z')
        except Exception:
            pass

        try:
            wow = value.split('/')[-1]
            woww = wow.split('.')[-2]

            with open(value, "rb") as file:
                gma = GMAVerifiedContents.parse_stream(file)
                Path(GMAD_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
                total = len(gma.content.all_file_meta) - 1

                def entries():
                    for i in range(0, total):
                        meta = gma.content.all_file_meta[i]
                        yield meta.data.file_name, gma.content.embedded_files.contents[i]

                self._write_entries_to_zip(entries(), total, f'{GMAD_OUTPUT_DIR}/{woww}.zip')

            self.label.pos_hint = {'center_x': 0.60, 'center_y': 0.90}
            self.label.color = (0, 1, 0, 1)
            self.dialog_dismisss()
            self.show_dialogg("Extracted!", f"Saved to {GMAD_OUTPUT_DIR}.")
        except ConstError:
            self.label.color = (1, 0, 0, 1)
            self.label.pos_hint = {'center_x': 0.60, 'center_y': 0.90}
            self.dialog_dismisss()
            self.show_dialogg("Error", "This is not a GMAD file. See the Errors section for help.")
            return
        except IndexError:
            self.label.color = (1, 0, 0, 1)
            self.label.pos_hint = {'center_x': 0.60, 'center_y': 0.90}
            self.dialog_dismisss()
            self.show_dialogg("Error", "Make sure you entered the correct path to your .gma file.")
            return
        except FileNotFoundError:
            self.label.color = (1, 0, 0, 1)
            self.label.pos_hint = {'center_x': 0.60, 'center_y': 0.90}
            self.dialog_dismisss()
            self.show_dialogg("Error", "Please grant file permissions, or the file does not exist.")
            return
        except Exception as fe:
            self.label.color = (1, 0, 0, 1)
            self.label.pos_hint = {'center_x': 0.58, 'center_y': 0.90}
            self.dialog_dismisss()
            self.show_dialogg("Error", f"Error: {fe}")
            self.label.text = str(fe)
            return

    def switch_to_second_layout(self, instance):
        self.screen_manager.current = "second"

    def switch_to_main_layout(self, instance):
        self.screen_manager.current = "main"

    def maybe_show_startup_dialog(self, *args):
        flag_path = os.path.join(self.user_data_dir, 'no_startup_dialog.flag')
        if os.path.exists(flag_path):
            return

        self.startup_checkbox = MDCheckbox(size_hint=(None, None), size=('32dp', '32dp'))

        checkbox_row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing='8dp')
        checkbox_row.add_widget(self.startup_checkbox)
        checkbox_row.add_widget(MDLabel(text="Don't show this again"))

        content = make_adaptive_box(
            make_dialog_text_label(
                "Latest Update\n\n"
                "- Removed the Workshop Downloader (i’ll probably make it a standalone app).\n"
                "- Updated UI\n"
                "- Faster extraction\n"
                "- Bug fixes and overall stability improvements"
            ),
            checkbox_row,
        )

        self.startup_dialog = MDDialog(
            title="Gmad 2.0",
            type="custom",
            auto_dismiss=False,
            content_cls=content,
            buttons=[
                MDFlatButton(text="Join Discord", on_release=self.open_discord_link),
                MDFlatButton(text="OK", on_release=self.close_startup_dialog),
            ],
        )
        self.startup_dialog.open()

    def close_startup_dialog(self, instance):
        if self.startup_checkbox.active:
            try:
                os.makedirs(self.user_data_dir, exist_ok=True)
                with open(os.path.join(self.user_data_dir, 'no_startup_dialog.flag'), 'w') as f:
                    f.write('1')
            except Exception:
                pass
        self.startup_dialog.dismiss()


MainApp().run()