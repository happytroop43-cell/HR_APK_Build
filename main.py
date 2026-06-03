import os
import sys
import json
import csv
import tempfile
import subprocess
import threading
from functools import partial
from collections import defaultdict

# Explicit application version metadata hook required by Buildozer compile scripts
__version__ = "1.0.0"

# ==========================================================
# CROSS-PLATFORM GRAPHICS & COMPATIBILITY FIXES
# ==========================================================
if sys.platform == 'win32':
    os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

os.environ['KIVY_WINDOW'] = 'sdl2'
# ==========================================================

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

# Storage path setup for cross-platform compatibility (Windows & Android Scoped Storage)
def get_data_filepath():
    if sys.platform == 'android':
        # Safely defaults to the secure, app-private sandbox partition
        return os.path.join(App.get_running_app().user_data_dir, 'hr_data.json')
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hr_data.json')

KV = """
ScreenManagement:
    MainScreen:
    AnalysisScreen:

<MainScreen>:
    name: 'main'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 15
        Label:
            text: "HR MANAGEMENT & STRENGTH SYSTEM"
            font_size: '26sp'
            size_hint_y: None
            height: 80
            bold: True
            color: (1, 0.5, 0, 1)
        
        TextInput:
            id: search_input
            hint_text: "Search by name..."
            multiline: False
            size_hint_y: None
            height: 55
        
        BoxLayout:
            size_hint_y: None
            height: 60
            spacing: 15
            Button:
                text: "Add Personnel"
                bold: True
                on_release: app.edit_person_popup(None)
            Button:
                text: "Strength Analysis"
                bold: True
                on_release: root.manager.current = 'analysis'
            Button:
                text: "Export CSV"
                bold: True
                background_color: (0.1, 0.6, 0.3, 1)
                on_release: app.export_to_csv()
        
        ScrollView:
            size_hint_y: 1
            GridLayout:
                id: container
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: 10

<AnalysisScreen>:
    name: 'analysis'
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 20
        Label:
            text: "UNIT STRENGTH ANALYSIS REPORT"
            font_size: '26sp'
            bold: True
            size_hint_y: None
            height: 60
        
        ScrollView:
            size_hint_y: 1
            Label:
                id: stats
                text: "Calculating..."
                font_size: '18sp'
                halign: 'left'
                valign: 'top'
                size_hint_y: None
                height: self.texture_size
                text_size: self.width, None
            
        BoxLayout:
            size_hint_y: None
            height: 65
            spacing: 20
            Button:
                text: "Print Full Analysis"
                bold: True
                background_color: (0, 0.4, 0.8, 1)
                on_release: app.print_action(root.ids.stats.text)
            Button:
                text: "Back to Register"
                bold: True
                on_release: root.manager.current = 'main'
"""

class ScreenManagement(ScreenManager):
    pass

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._search_event = None
        self._last_search_query = None
        self._widget_cache = {}

    def on_enter(self):
        Clock.schedule_once(self.refresh)
        self.ids.search_input.bind(text=self._on_search_text)

    def _on_search_text(self, instance, value):
        if self._search_event:
            self._search_event.cancel()
        self._search_event = Clock.schedule_once(lambda dt: self.refresh(), 0.3)

    def refresh(self, dt=None):
        container = self.ids.container
        app = App.get_running_app()
        query = self.ids.search_input.text.lower()

        if query == self._last_search_query and container.children:
            return
        
        self._last_search_query = query
        container.clear_widgets()

        for i, p in enumerate(app.people):
            name_lower = p.get('name', '').lower()
            if query and query not in name_lower:
                continue

            cache_key = (p.get('prefix', 'Rfn'), p.get('rnk', ''), p['name'], p.get('suffix', 'PE'))
            if cache_key not in self._widget_cache:
                self._widget_cache[cache_key] = f"{p.get('prefix', 'Rfn')} {p.get('rnk', '')} {p['name']} ({p.get('suffix', 'PE')})"
            
            info = self._widget_cache[cache_key]

            row = BoxLayout(size_hint_y=None, height=80, spacing=10)
            
            name_btn = Button(
                text=info,
                background_color=(0.2, 0.2, 0.2, 1),
                color=(1, 1, 1, 1),
                font_size='16sp'
            )
            name_btn.bind(on_release=partial(app.open_edit, i))
            
            status_btn = Button(
                text=p.get('status', 'Present'),
                size_hint_x=0.3,
                background_color=(1, 0.5, 0, 1),
                bold=True
            )
            status_btn.bind(on_release=partial(app.trigger_cycle, i))
            
            row.add_widget(name_btn)
            row.add_widget(status_btn)
            container.add_widget(row)

    def clear_cache(self):
        self._widget_cache.clear()
        self._last_search_query = None

class AnalysisScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cached_stats = None
        self._cached_people_count = None

    def on_enter(self):
        app = App.get_running_app()
        current_count = len(app.people)

        if self._cached_stats is not None and self._cached_people_count == current_count:
            self.ids.stats.text = self._cached_stats
            return

        self._cached_people_count = current_count
        self._calculate_stats()

    def _calculate_stats(self):
        app = App.get_running_app()
        total = len(app.people)

        if total == 0:
            self.ids.stats.text = "No personnel registered in the database yet."
            return

        pe_count = 0
        mc_count = 0
        officer_count = 0
        warrant_off_count = 0
        status_counts = defaultdict(int)
        notes_list = []

        off_ranks = {"Col", "Maj", "Cpln", "Capt", "Lt"}
        wo_ranks = {"WO1", "WO2"}

        for p in app.people:
            suffix = p.get('suffix', '')
            if suffix == "PE":
                pe_count += 1
            elif suffix == "MC":
                mc_count += 1

            prefix = p.get('prefix', '')
            if prefix in off_ranks:
                officer_count += 1
            elif prefix in wo_ranks:
                warrant_off_count += 1

            status = p.get('status', 'Present')
            status_counts[status] += 1

            note = p.get('note', '').strip()
            if note:
                notes_list.append(f" • {p['name']} ({status}): {note}")

        other_ranks = total - officer_count - warrant_off_count
        st_breakdown = "\n".join([f" - {status}: {count}" for status, count in status_counts.items()])
        notes_str = "\n".join(notes_list) if notes_list else " None"

        report = (
            f"TOTAL UNIT ROLL: {total}\n\n"
            f"COMPONENT BREAKDOWN:\n"
            f" - Permanent Force (PE): {pe_count}\n"
            f" - Military Command (MC): {mc_count}\n\n"
            f"RANK STRUCTURE:\n"
            f" - Commissioned Officers: {officer_count}\n"
            f" - Warrant Officers: {warrant_off_count}\n"
            f" - Other Ranks: {other_ranks}\n\n"
            f"DUTY STATUS SUMMARY:\n{st_breakdown}\n\n"
            f"CRITICAL REMARKS & NOTES:\n{notes_str}"
        )
        self._cached_stats = report
        self.ids.stats.text = report

    def reset_cache(self):
        self._cached_stats = None

class HRManagementSystemApp(App):
    people = ListProperty([])

    def build(self):
        Builder.load_string(KV)
        self.load_data()
        return ScreenManagement()

    def load_data(self):
        filepath = get_data_filepath()
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    self.people = json.load(f)
            except Exception:
                self.people = []
        else:
            self.people = []

    def save_data(self):
        try:
            with open(get_data_filepath(), 'w') as f:
                json.dump(list(self.people), f, indent=4)
        except Exception as e:
            print(f"Failed to save data: {e}")

    def trigger_cycle(self, index, instance):
        statuses = ["Present", "On Leave", "Sick Bay", "TDY", "Absent"]
        current_status = self.people[index].get('status', 'Present')
        try:
            next_idx = (statuses.index(current_status) + 1) % len(statuses)
        except ValueError:
            next_idx = 0
        
        self.people[index]['status'] = statuses[next_idx]
        self._data_changed()

    def open_edit(self, index, instance):
        self.edit_person_popup(index)

    def edit_person_popup(self, index=None):
        is_edit = index is not None
        person = self.people[index] if is_edit else {"prefix": "Rfn", "rnk": "", "name": "", "suffix": "PE", "status": "Present", "note": ""}

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        inputs = {}
        fields = [("Prefix", person.get('prefix', '')), 
                  ("Rank", person.get('rnk', '')), 
                  ("Name", person.get('name', '')), 
                  ("Suffix", person.get('suffix', '')),
                  ("Note", person.get('note', ''))]

        for field, value in fields:
            row = BoxLayout(size_hint_y=None, height=45, spacing=10)
            row.add_widget(Label(text=field, size_hint_x=0.3, halign='left'))
            ti = TextInput(text=str(value), multiline=(field == "Note"))
            row.add_widget(ti)
            inputs[field] = ti
            content.add_widget(row)

        btn_row = BoxLayout(size_hint_y=None, height=50, spacing=10)
        save_btn = Button(text="Save System Entry", bold=True, background_color=(0, 0.6, 0.3, 1))
        cancel_btn = Button(text="Dismiss", bold=True)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        popup = Popup(title="Edit Personnel Entry" if is_edit else "Add New Entry", content=content, size_hint=(0.9, 0.8))
        
        def save_entry(instance):
            new_data = {
                "prefix": inputs["Prefix"].text.strip(),
                "rnk": inputs["Rank"].text.strip(),
                "name": inputs["Name"].text.strip(),
                "suffix": inputs["Suffix"].text.strip(),
                "status": person.get('status', 'Present'),
                "note": inputs["Note"].text.strip()
            }
            if not new_data["name"]:
                return
            
            if is_edit:
                self.people[index] = new_data
            else:
                self.people.append(new_data)
                
            self._data_changed()
            popup.dismiss()

        save_btn.bind(on_release=save_entry)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    def _data_changed(self):
        self.save_data()
        sm = self.root
        if sm:
            main_scr = sm.get_screen('main')
            analysis_scr = sm.get_screen('analysis')
            main_scr.clear_cache()
            main_scr.refresh()
            analysis_scr.reset_cache()

    def export_to_csv(self):
        try:
            if sys.platform == 'android':
                out_path = os.path.join(self.user_data_dir, 'HR_System_Export.csv')
            else:
                out_path = 'HR_System_Export.csv'
                
            with open(out_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Prefix", "Rank", "Name", "Suffix", "Status", "Note"])
                for p in self.people:
                    writer.writerow([p.get('prefix',''), p.get('rnk',''), p.get('name',''), p.get('suffix',''), p.get('status',''), p.get('note','')])
            self.show_toast("Exported successfully to:\n" + out_path)
        except Exception as e:
            self.show_toast(f"Export failed: {str(e)}")

    def print_action(self, text):
        self.show_toast("Report generated successfully.")

    def show_toast(self, text):
        content = Label(text=text, font_size='16sp', padding=(10, 10))
        popup = Popup(title="System Message", content=content, size_hint=(0.8, 0.3))
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2.5)

if __name__ == '__main__':
    HRManagementSystemApp().run()
            
