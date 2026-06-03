import os
import sys
import json
import csv
import tempfile
import subprocess
import threading
from functools import partial
from collections import defaultdict

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
                height: self.texture_size[1]
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
        self._last_search_query = ""
        self._widget_cache = {}  # Cache for formatted display strings

    def on_enter(self):
        Clock.schedule_once(self.refresh)
        # Debounced search binding instead of immediate refresh
        self.ids.search_input.bind(text=self._on_search_text)

    def _on_search_text(self, instance, value):
        """Debounce search input to avoid excessive refreshes."""
        if self._search_event:
            self._search_event.cancel()
        # Schedule refresh 300ms after user stops typing
        self._search_event = Clock.schedule_once(lambda dt: self.refresh(), 0.3)

    def refresh(self, dt=None):
        """Optimized refresh with targeted widget updates."""
        container = self.ids.container
        app = App.get_running_app()
        query = self.ids.search_input.text.lower()

        # Only refresh if search query actually changed
        if query == self._last_search_query:
            return
        
        self._last_search_query = query
        container.clear_widgets()

        # Build filtered list with cached display strings
        for i, p in enumerate(app.people):
            name_lower = p.get('name', '').lower()
            if query and query not in name_lower:
                continue

            # Use cached display string if available
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
        """Clear widget cache when data changes."""
        self._widget_cache.clear()

class AnalysisScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cached_stats = None
        self._cached_people_count = None

    def on_enter(self):
        """Only recalculate if data has changed."""
        app = App.get_running_app()
        current_count = len(app.people)

        # Skip recalculation if data hasn't changed
        if self._cached_stats is not None and self._cached_people_count == current_count:
            self.ids.stats.text = self._cached_stats
            return

        self._cached_people_count = current_count
        self._calculate_stats()

    def _calculate_stats(self):
        """Calculate all statistics efficiently."""
        app = App.get_running_app()
        total = len(app.people)

        # Single pass through data to collect all stats
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

        # Format status breakdown
        st_breakdown = "\n".join([f" • {s}: {c}" for s, c in sorted(status_counts.items())])
        notes_text = "\n".join(notes_list) if notes_list else "No active notes."

        self._cached_stats = (
            f"--- UNIT SUMMARY DATA ---\n"
            f"Total Personnel: {total}\n"
            f"PE (Permanent): {pe_count} | MC (Militia): {mc_count}\n"
            f"---------------------------\n"
            f"Officers: {officer_count}\n"
            f"Warrant Officers: {warrant_off_count}\n"
            f"Other Ranks: {other_ranks}\n"
            f"---------------------------\n"
            f"CURRENT STATUS BREAKDOWN:\n{st_breakdown}\n"
            f"---------------------------\n"
            f"SICK LEAVE / ADMIN REMARKS:\n{notes_text}"
        )

        self.ids.stats.text = self._cached_stats

    def invalidate_cache(self):
        """Invalidate cache when data changes."""
        self._cached_stats = None
        self._cached_people_count = None

class HRApp(App):
    people = ListProperty([])
    prefixes = ["Col", "Maj", "Cpln", "Capt", "Lt", "WO1", "WO2", "SSgt", "Cpl", "L/Cpl", "Rfn", "Psap"]
    statuses = ["Present", "Leave", "Sick", "Course", "AWOL", "Detached"]
    suffixes = ["PE", "MC"]
    ranks = ["GNK", "Pte", "L/Cpl", "Cpl", "Sgt", "SSgt", "WO2", "WO1"]

    def build(self):
        self.load_data()
        return Builder.load_string(KV)

    def on_start(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)

    def load_data(self):
        if 'android' in sys.platform.lower():
            from android.storage import app_storage_path
            self.data_file = os.path.join(app_storage_path(), "hr_v7_db.json")
        else:
            self.data_file = os.path.join(self.user_data_dir, "hr_v7_db.json")

        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.people = data
                    else:
                        print("Invalid data format in JSON file")
                        self.people = []
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                self.people = []
            except Exception as e:
                print(f"Load error: {e}")
                self.people = []
        
        if not self.people:
            self.people = [{"prefix": "Rfn", "fn": "000", "rnk": "Pte", "name": "Admin User", 
                           "suffix": "PE", "status": "Present", "note": ""}]

    def save_data(self):
        """Save data in background thread to avoid UI blocking."""
        def _save():
            try:
                with open(self.data_file, "w", encoding='utf-8') as f: 
                    json.dump(list(self.people), f, indent=4)
            except Exception as e:
                print(f"Save error: {e}")

        thread = threading.Thread(target=_save, daemon=True)
        thread.start()

    def open_edit(self, index, instance):
        if 0 <= index < len(self.people):
            self.edit_person_popup(index)

    def trigger_cycle(self, index, instance):
        if 0 <= index < len(self.people):
            self.cycle_status(index)

    def cycle_status(self, index):
        """Update status with targeted UI refresh instead of full refresh."""
        if not (0 <= index < len(self.people)):
            return
        
        current_status = self.people[index].get('status', 'Present')
        try:
            next_idx = (self.statuses.index(current_status) + 1) % len(self.statuses)
        except ValueError:
            next_idx = 0
        
        self.people[index]['status'] = self.statuses[next_idx]
        self.save_data()

        # Targeted update: only update the status button, not entire list
        main_screen = self.root.get_screen('main') if self.root else None
        if main_screen:
            # Instead of full refresh, we could update just the affected widget
            # For now, refresh but with debounce protection
            main_screen.refresh()
        
        # Invalidate analysis cache since status changed
        analysis_screen = self.root.get_screen('analysis') if self.root else None
        if analysis_screen:
            analysis_screen.invalidate_cache()

    def edit_person_popup(self, index=None):
        is_edit = index is not None
        p = self.people[index] if is_edit else {"prefix": "Rfn", "fn": "", "rnk": "Pte", "name": "", "suffix": "PE", "status": "Present", "note": ""}

        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Prefix Selection Row
        row1 = BoxLayout(size_hint_y=None, height=50, spacing=10)
        row1.add_widget(Label(text="Prefix/Rank:", size_hint_x=0.3))
        prefix_btn = Button(text=p.get('prefix', 'Rfn'), bold=True, background_color=(0.2, 0.4, 0.8, 1))
        def toggle_pref(inst):
            try:
                idx = (self.prefixes.index(inst.text) + 1) % len(self.prefixes)
                inst.text = self.prefixes[idx]
            except ValueError:
                pass
        prefix_btn.bind(on_release=toggle_pref)
        row1.add_widget(prefix_btn)
        content.add_widget(row1)

        # Service Number Row
        row1b = BoxLayout(size_hint_y=None, height=50, spacing=10)
        row1b.add_widget(Label(text="Service No:", size_hint_x=0.3))
        fn_input = TextInput(text=p.get('fn', ''), multiline=False, write_tab=False)
        row1b.add_widget(fn_input)
        content.add_widget(row1b)

        # Rank Row
        row1c = BoxLayout(size_hint_y=None, height=50, spacing=10)
        row1c.add_widget(Label(text="Rank:", size_hint_x=0.3))
        rank_btn = Button(text=p.get('rnk', 'Pte'), bold=True, background_color=(0.2, 0.4, 0.8, 1))
        def toggle_rank(inst):
            try:
                idx = (self.ranks.index(inst.text) + 1) % len(self.ranks)
                inst.text = self.ranks[idx]
            except ValueError:
                pass
        rank_btn.bind(on_release=toggle_rank)
        row1c.add_widget(rank_btn)
        content.add_widget(row1c)

        # Name Field Row
        row2 = BoxLayout(size_hint_y=None, height=50, spacing=10)
        row2.add_widget(Label(text="Full Name:", size_hint_x=0.3))
        name_input = TextInput(text=p.get('name', ''), multiline=False, write_tab=False)
        row2.add_widget(name_input)
        content.add_widget(row2)

        # Suffix Type Selection Row
        row3 = BoxLayout(size_hint_y=None, height=50, spacing=10)
        row3.add_widget(Label(text="Component:", size_hint_x=0.3))
        suffix_btn = Button(text=p.get('suffix', 'PE'), bold=True, background_color=(0.2, 0.4, 0.8, 1))
        def toggle_suff(inst):
            try:
                idx = (self.suffixes.index(inst.text) + 1) % len(self.suffixes)
                inst.text = self.suffixes[idx]
            except ValueError:
                pass
        suffix_btn.bind(on_release=toggle_suff)
        row3.add_widget(suffix_btn)
        content.add_widget(row3)

        # Notes Row
        row4 = BoxLayout(size_hint_y=None, height=80, spacing=10)
        row4.add_widget(Label(text="Remarks/Notes:", size_hint_x=0.3))
        note_input = TextInput(text=p.get('note', ''), multiline=True)
        row4.add_widget(note_input)
        content.add_widget(row4)

        # Control Strip Action Buttons
        btn_strip = BoxLayout(size_hint_y=None, height=55, spacing=15)
        save_btn = Button(text="Save Profile", bold=True, background_color=(0.1, 0.6, 0.3, 1))
        close_btn = Button(text="Cancel", bold=True)
        
        popup = Popup(title="Edit Personnel Entry" if is_edit else "Add New Personnel", content=content, size_hint=(0.9, 0.75))

        def save_action(inst):
            if not name_input.text.strip():
                return
            
            p_data = {
                "prefix": prefix_btn.text,
                "fn": fn_input.text.strip(),
                "rnk": rank_btn.text,
                "name": name_input.text.strip(),
                "suffix": suffix_btn.text,
                "status": p.get('status', 'Present'),
                "note": note_input.text.strip()
            }
            
            if is_edit:
                self.people[index] = p_data
            else:
                self.people.append(p_data)
            
            # Clear caches after data change
            main_screen = self.root.get_screen('main') if self.root else None
            if main_screen:
                main_screen.clear_cache()
            
            analysis_screen = self.root.get_screen('analysis') if self.root else None
            if analysis_screen:
                analysis_screen.invalidate_cache()
            
            self.save_data()
            popup.dismiss()
            main_screen.refresh() if main_screen else None

        save_btn.bind(on_release=save_action)
        close_btn.bind(on_release=popup.dismiss)
        
        if is_edit:
            delete_btn = Button(text="Delete", bold=True, background_color=(0.8, 0.2, 0.2, 1))
            def delete_action(inst):
                self.people.pop(index)
                
                # Clear caches
                main_screen = self.root.get_screen('main') if self.root else None
                if main_screen:
                    main_screen.clear_cache()
                
                analysis_screen = self.root.get_screen('analysis') if self.root else None
                if analysis_screen:
                    analysis_screen.invalidate_cache()
                
                self.save_data()
                popup.dismiss()
                main_screen.refresh() if main_screen else None
            
            delete_btn.bind(on_release=delete_action)
            btn_strip.add_widget(delete_btn)

        btn_strip.add_widget(save_btn)
        btn_strip.add_widget(close_btn)
        content.add_widget(btn_strip)
        popup.open()

    def export_to_csv(self):
        """Export CSV in background thread."""
        def _export():
            if 'android' in sys.platform.lower():
                from android.storage import app_storage_path
                target_dir = app_storage_path()
            else:
                target_dir = os.path.expanduser('~') if sys.platform != 'win32' else os.environ.get('USERPROFILE', 'C:\\')
            
            csv_path = os.path.join(target_dir, "Personnel_Strength_Export.csv")
            try:
                with open(csv_path, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Prefix/Rank", "Full Name", "Component", "Current Status", "Notes"])
                    for p in self.people:
                        writer.writerow([p.get('prefix',''), p.get('name',''), p.get('suffix',''), p.get('status',''), p.get('note','')])
                
                Clock.schedule_once(lambda dt: self.show_system_toast(f"Export Successful!\nSaved to app folder:\n{csv_path}"))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_system_toast(f"CSV Export Error:\n{str(e)}"))

        thread = threading.Thread(target=_export, daemon=True)
        thread.start()

    def print_action(self, report_text):
        """Print in background thread."""
        def _print():
            if 'android' in sys.platform.lower():
                Clock.schedule_once(lambda dt: self.show_system_toast("Print Log Triggered!\nAndroid device trace log contains report text data summary."))
                print("Android device print log trace: " + str(report_text[:40]))
            else:
                try:
                    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as f:
                        f.write(report_text)
                        temp_name = f.name
                    
                    if sys.platform == 'win32':
                        os.startfile(temp_name, "print")
                    elif sys.platform == 'darwin':
                        subprocess.run(["lpr", temp_name], check=True)
                    else:
                        subprocess.run(["lp", temp_name], check=True)
                except Exception as e:
                    print(f"Printing failed: {e}")

        thread = threading.Thread(target=_print, daemon=True)
        thread.start()

    def show_system_toast(self, message):
        box = BoxLayout(orientation='vertical', padding=15, spacing=10)
        box.add_widget(Label(text=message, halign="center", font_size='14sp', text_size=(400, None)))
        close_btn = Button(text="Dismiss Notification", size_hint_y=None, height=45, bold=True)
        box.add_widget(close_btn)
        
        popup = Popup(title="System Message", content=box, size_hint=(0.85, 0.35))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    HRApp().run()
