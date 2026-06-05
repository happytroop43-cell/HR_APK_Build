import os
import sys

# Suppress low-level Linux hardware touch device probes permanently to avoid crashes
os.environ['KIVY_NO_ENV_CONFIG'] = '1'
os.environ['KIVY_NO_ARGS'] = '1'

from kivy.config import Config  # noqa: E402
Config.set('input', 'mouse', 'mouse,disable_multitouch')

import json  # noqa: E402
import csv  # noqa: E402
import webbrowser  # noqa: E402
import tempfile  # noqa: E402
import subprocess  # noqa: E402
from kivy.app import App  # noqa: E402
from kivy.uix.screenmanager import ScreenManager, Screen  # noqa: E402
from kivy.lang import Builder  # noqa: E402
from kivy.properties import ListProperty  # noqa: E402
from kivy.core.window import Window  # noqa: E402
from kivy.clock import Clock  # noqa: E402
from kivy.uix.button import Button  # noqa: E402
from kivy.uix.popup import Popup  # noqa: E402
from kivy.uix.textinput import TextInput  # noqa: E402
from kivy.uix.boxlayout import BoxLayout  # noqa: E402
from kivy.uix.gridlayout import GridLayout  # noqa: E402
from kivy.uix.label import Label  # noqa: E402
from kivy.uix.filechooser import FileChooserIconView  # noqa: E402
from kivy.uix.scrollview import ScrollView  # noqa: E402
from kivy.uix.dropdown import DropDown  # noqa: E402

# Clean light gray backdrop canvas setup
Window.clearcolor = (0.92, 0.94, 0.96, 1)

KV = """
#:import os os

ScreenManagement:
    MainScreen:
    AnalysisScreen:
    DocumentManagerScreen:

<MainScreen>:
    name: 'main'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 15
        
        # TOP PERSISTENT UTILITY HUB MENU BAR
        BoxLayout:
            size_hint_y: None
            height: 55
            spacing: 10
            canvas.before:
                Color:
                    rgba: 0.12, 0.23, 0.35, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Button:
                text: "📥 Import CSV"
                bold: True
                background_color: (0.18, 0.49, 0.73, 1)
                on_release: app.import_excel_popup()
            Button:
                text: "📤 Export CSV"
                bold: True
                background_color: (0.15, 0.68, 0.38, 1)
                on_release: app.export_to_excel()
            Button:
                text: "🧹 Wipe Database"
                bold: True
                background_color: (0.75, 0.22, 0.17, 1)
                on_release: app.confirm_clear_popup()

        Label:
            text: "HR MANAGEMENT & STRENGTH SYSTEM"
            font_size: '24sp'
            size_hint_y: None
            height: 50
            bold: True
            color: (0.12, 0.23, 0.35, 1)
        
        TextInput:
            id: search_input
            hint_text: "Search roster by name..."
            multiline: False
            size_hint_y: None
            height: 45
            background_color: (1, 1, 1, 1)
            foreground_color: (0.1, 0.1, 0.1, 1)
            on_text: root.refresh()
        
        BoxLayout:
            size_hint_y: None
            height: 50
            spacing: 15
            Button:
                text: "➕ Add Personnel Profile"
                bold: True
                background_color: (0.12, 0.23, 0.35, 1)
                on_release: app.edit_person_popup(None)
            Button:
                text: "🖼️ Document Viewer Hub"
                bold: True
                background_color: (0.18, 0.49, 0.73, 1)
                on_release: root.manager.current = 'doc_manager'
            Button:
                text: "📊 Strength Matrix"
                bold: True
                background_color: (0.12, 0.23, 0.35, 1)
                on_release: root.manager.current = 'analysis'
        
        # MAIN REGISTER SCROLL VIEW BAR
        ScrollView:
            do_scroll_x: False
            do_scroll_y: True
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
        padding: 25
        spacing: 15
        Label:
            text: "UNIT STRENGTH ANALYSIS REPORT"
            font_size: '24sp'
            bold: True
            size_hint_y: None
            height: 50
            color: (0.12, 0.23, 0.35, 1)
        
        ScrollView:
            do_scroll_x: False
            do_scroll_y: True
            Label:
                id: stats
                text: "Running Matrix Calculations..."
                font_size: '14sp'
                halign: 'left'
                valign: 'top'
                color: (0.15, 0.2, 0.25, 1)
                size_hint_y: None
                height: max(self.texture_size[1], self.parent.height if self.parent else 500)
                text_size: self.width, None
            
        BoxLayout:
            size_hint_y: None
            height: 55
            spacing: 20
            Button:
                text: "🖨️ Print Full Analysis"
                bold: True
                background_color: (0.18, 0.49, 0.73, 1)
                on_release: app.print_action(stats.text)
            Button:
                text: "🔙 Back to Register"
                bold: True
                background_color: (0.5, 0.55, 0.6, 1)
                on_release: root.manager.current = 'main'

<DocumentManagerScreen>:
    name: 'doc_manager'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 15
        
        Label:
            id: doc_title
            text: "🖼️ USB IMAGES & SICK NOTE MEDIA DOCUMENT HUB"
            font_size: '22sp'
            bold: True
            size_hint_y: None
            height: 45
            color: (0.12, 0.23, 0.35, 1)
            
        BoxLayout:
            orientation: 'horizontal'
            spacing: 20
            
            BoxLayout:
                orientation: 'vertical'
                spacing: 10
                size_hint_x: 0.45
                FileChooserIconView:
                    id: filechooser
                    filters: ['*.png', '*.jpg', '*.jpeg']
                    path: "/media" if os.path.exists("/media") else os.path.expanduser("~")
                Button:
                    text: "Load Image File"
                    size_hint_y: None
                    height: 45
                    bold: True
                    background_color: (0.18, 0.49, 0.73, 1)
                    on_release: root.load_selected_file()
            
            BoxLayout:
                orientation: 'vertical'
                spacing: 10
                size_hint_x: 0.55
                canvas.before:
                    Color:
                        rgba: 0.88, 0.9, 0.93, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                Image:
                    id: preview_image
                    source: ''
                    
        BoxLayout:
            size_hint_y: None
            height: 55
            spacing: 20
            Button:
                text: "🖨️ Hardware Print Document"
                bold: True
                background_color: (0.15, 0.68, 0.38, 1)
                on_release: root.print_current_document()
            Button:
                text: "🔙 Return to Main Register"
                bold: True
                background_color: (0.5, 0.55, 0.6, 1)
                on_release: root.manager.current = 'main'
"""

class ScreenManagement(ScreenManager):
    pass


class MainScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.refresh)

    def refresh(self, dt=None):
        container = self.ids.container
        container.clear_widgets()
        app = App.get_running_app()
        query = self.ids.search_input.text.lower()
        
        for i, p in enumerate(app.people):
            if query in p['name'].lower():
                row = BoxLayout(size_hint_y=None, height=75, spacing=10)
                
                info = f" [{p.get('prefix', 'Rfn')}] {p.get('rnk', '')} {p['name']} ({p.get('suffix', 'PE')})"
                name_btn = Button(text=info, background_color=(1, 1, 1, 1), color=(0.12, 0.23, 0.35, 1), halign='left', valign='center', font_size='15sp')
                name_btn.text_size = (Window.width * 0.45, None)
                name_btn.bind(on_release=lambda x, idx=i: app.edit_person_popup(idx))
                
                doc_btn = Button(text="📎 Docs", size_hint_x=0.18, background_color=(0.5, 0.55, 0.6, 1), bold=True)
                doc_btn.bind(on_release=lambda x, idx=i: app.document_manager_popup(idx))
                
                status_btn = Button(text=p['status'], size_hint_x=0.28, background_color=(0.18, 0.49, 0.73, 1), color=(1, 1, 1, 1), bold=True)
                status_btn.bind(on_release=lambda x, idx=i: app.cycle_status(idx))
                
                row.add_widget(name_btn)
                row.add_widget(doc_btn)
                row.add_widget(status_btn)
                container.add_widget(row)


class AnalysisScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        
        def make_matrix_bucket():
            return {
                "Total": 0, "PE": 0, "MC": 0, "CA": 0,
                "Officers": {"Total": 0, "PE": 0, "MC": 0, "CA": 0},
                "Warrant_Officers": {"Total": 0, "PE": 0, "MC": 0, "CA": 0},
                "Nco_Ranks": {"Total": 0, "PE": 0, "MC": 0, "CA": 0},
                "Rfn": {"Total": 0, "PE": 0, "MC": 0, "CA": 0},
                "PSAP": {"Total": 0, "PE": 0, "MC": 0, "CA": 0}
            }

        generic = make_matrix_bucket()
        effective = make_matrix_bucket()
        non_effective = make_matrix_bucket()
        
        leaves_breakdown = {status: make_matrix_bucket() for status in app.statuses if status != "Present"}
        
        off_ranks = ["Colonel", "Major", "Chaplain", "Capt", "Lt"]
        wo_ranks = ["MWO", "WO1", "WO2"]
        nco_ranks = ["Ssgt", "Sgt", "Cpl", "L/Cpl"]
        pte_ranks = ["Rfn"]
        psap_ranks = ["PSAP"]

        for p in app.people:
            pref = p.get('prefix', 'Rfn')
            suff = p.get('suffix', 'PE')
            if suff not in ["PE", "MC", "CA"]:
                suff = "PE"
            stat = p.get('status', 'Present')
            
            if pref in off_ranks:
                group = "Officers"
            elif pref in wo_ranks:
                group = "Warrant_Officers"
            elif pref in nco_ranks:
                group = "Nco_Ranks"
            elif pref in pte_ranks:
                group = "Rfn"
            elif pref in psap_ranks:
                group = "PSAP"
            

            # Generic Calculations
            generic["Total"] += 1
            generic[suff] = generic.get(suff, 0) + 1
            generic[group]["Total"] += 1
            generic[group][suff] = generic[group].get(suff, 0) + 1

            # Effective vs Non-Effective
            if stat == "Present":
                effective["Total"] += 1
                effective[suff] = effective.get(suff, 0) + 1
                effective[group]["Total"] += 1
                effective[group][suff] = effective[group].get(suff, 0) + 1
            else:
                non_effective["Total"] += 1
                non_effective[suff] = non_effective.get(suff, 0) + 1
                non_effective[group]["Total"] += 1
                non_effective[group][suff] = non_effective[group].get(suff, 0) + 1
                
                if stat in leaves_breakdown:
                    leaves_breakdown[stat]["Total"] += 1
                    leaves_breakdown[stat][suff] = leaves_breakdown[stat].get(suff, 0) + 1
                    leaves_breakdown[stat][group]["Total"] += 1
                    leaves_breakdown[stat][group][suff] = leaves_breakdown[stat][group].get(suff, 0) + 1

        report = []
        report.append("==========================================================================")
        report.append("                       UNIT STRENGTH ANALYSIS REPORT                      ")
        report.append("==========================================================================")
        
        def format_section(title, data):
            lines = [f"\n🔹 {title.upper()}"]
            lines.append(f"  • Total Strength : {data['Total']} (PE: {data.get('PE', 0)} | MC: {data.get('MC', 0)} | CA: {data.get('CA', 0)})")
            for sub in ["Officers", "Warrant_Officers", "Nco_Ranks", "Rfn", "PSAP"]:
                name = sub.replace("_", " ")
                lines.append(f"    - {name:<16}: {data[sub]['Total']} [PE: {data[sub].get('PE',0)} | MC: {data[sub].get('MC',0)}]")
            return "\n".join(lines)

        report.append(format_section("Generic Roster Summary (All Ramifications)", generic))
        report.append(format_section("Effective Strength (Present Duty)", effective))
        report.append(format_section("Non-Effective Strength (All Absences combined)", non_effective))
        
        report.append("\n==========================================================================")
        report.append("                    GRANULAR ABSENCE LEAVE BREAKDOWN                     ")
        report.append("==========================================================================")
        for stat, bucket in leaves_breakdown.items():
            if bucket["Total"] > 0:
                report.append(format_section(f"Status Category: {stat}", bucket))
        
        self.ids.stats.text = "\n".join(report)


class DocumentManagerScreen(Screen):
    current_doc_path = ""

    def on_enter(self):
        self.ids.filechooser.path = os.path.expanduser("~")

    def load_selected_file(self):
        selection = self.ids.filechooser.selection
        if selection:
            target_path = selection[0]
            if target_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.current_doc_path = target_path
                self.ids.preview_image.source = target_path
                self.ids.preview_image.reload()
                self.ids.doc_title.text = f"📄 Active Image: {os.path.basename(target_path)}"
            else:
                self.ids.doc_title.text = "⚠️ Viewport preview window supports image files only!"
        else:
            self.ids.doc_title.text = "⚠️ Select a file before clicking load!"

    def print_current_document(self):
        if self.current_doc_path:
            App.get_running_app().print_image_file(self.current_doc_path)
        else:
            self.ids.doc_title.text = "❌ No active document loaded to print!"

class HRStrengthApp(App):
    people = ListProperty([])
    ranks = ListProperty(["Colonel", "Major", "Chaplain", "Capt", "Lt", "MWO", "WO1", "WO2", "Ssgt", "Sgt", "Cpl", "L/Cpl", "Rfn", "PSAP"])
    statuses = ListProperty(["Present", "Family Responsibility", "Detatched Duty", "Awol", "Course", "Study leave", "Special Leave", "Temp Incapacity", "Hospital", "OI", "OE", "Sick Leave", "Medical appointment", "Death", "Vacation"])
    
    db_file = "personnel_db.json"
    docs_dir = "attached_documents"

    def build(self):
        self.load_database()
        return Builder.load_string(KV)

    def load_database(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    self.people = json.load(f)
            except Exception as e:
                print(f"Error loading DB: {e}")
                self.people = []
        else:
            self.people = [
                {"prefix": "Major", "rnk": "Officer", "name": "John Doe", "suffix": "PE", "status": "Present", "attached_document": ""},
                {"prefix": "Rfn", "rnk": "Rifleman", "name": "Jane Smith", "suffix": "MC", "status": "Sick Leave", "attached_document": ""}
            ]
            self.save_database()

    def save_database(self):
        try:
            with open(self.db_file, 'w') as f:
                json.dump(list(self.people), f, indent=4)
        except Exception as e:
            print(f"Error saving DB: {e}")

    def cycle_status(self, index):
        current_status = self.people[index]['status']
        try:
            curr_idx = self.statuses.index(current_status)
            next_idx = (curr_idx + 1) % len(self.statuses)
        except ValueError:
            next_idx = 0
            
        self.people[index]['status'] = self.statuses[next_idx]
        self.save_database()
        self.root.get_screen('main').refresh()

    def get_document_path(self, filename):
        if not os.path.exists(self.docs_dir):
            os.makedirs(self.docs_dir)
        return os.path.join(self.docs_dir, filename)

    # 📋 PERSONNEL RECORD PROFILE EDITOR POPUP WINDOW
    def edit_person_popup(self, index=None):
        is_edit = index is not None
        person = self.people[index] if is_edit else {"prefix": "Rfn", "rnk": "", "name": "", "suffix": "PE", "status": "Present", "attached_document": ""}

        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=220)
        
        # Rank/Prefix Selection Dropdown configuration
        grid.add_widget(Label(text="Rank Group:", bold=True))
        pref_btn = Button(text=person.get('prefix', 'Rfn'))
        pref_dropdown = DropDown()
        for r in self.ranks:
            btn = Button(text=r, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn: pref_dropdown.select(btn.text))
            pref_dropdown.add_widget(btn)
        pref_btn.bind(on_release=pref_dropdown.open)
        pref_dropdown.bind(on_select=lambda instance, x: setattr(pref_btn, 'text', x))
        grid.add_widget(pref_btn)
        
        grid.add_widget(Label(text="Rank Group:", bold=True))
        txt_rnk = TextInput(text=person.get('rnk', ''), multiline=False)
        grid.add_widget(txt_rnk)
        
        grid.add_widget(Label(text="Full Name String:", bold=True))
        txt_name = TextInput(text=person.get('name', ''), multiline=False)
        grid.add_widget(txt_name)
        
        # Suffix Selection Dropdown Configuration
        grid.add_widget(Label(text="Suffix Group:", bold=True))
        suff_btn = Button(text=person.get('suffix', 'PE'))
        suff_dropdown = DropDown()
        for s in ["PE", "MC", "CA"]:
            btn = Button(text=s, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn: suff_dropdown.select(btn.text))
            suff_dropdown.add_widget(btn)
        suff_btn.bind(on_release=suff_dropdown.open)
        suff_dropdown.bind(on_select=lambda instance, x: setattr(suff_btn, 'text', x))
        grid.add_widget(suff_btn)
        
        content.add_widget(grid)
        
        btn_layout = BoxLayout(size_hint_y=None, height=45, spacing=15)
        save_btn = Button(text="Save Profile Data", bold=True, background_color=(0.15, 0.68, 0.38, 1))
        cancel_btn = Button(text="Discard changes", bold=True, background_color=(0.75, 0.22, 0.17, 1))
        
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup = Popup(title="Personnel Profile Modification Utility" if is_edit else "Create New Profile Entry",
                      content=content, size_hint=(0.85, 0.65))
        
        def save_action(instance):
            cleaned_name = txt_name.text.strip()
            if not cleaned_name:
                return
            
            new_data = {
                "prefix": pref_btn.text,
                "rnk": txt_rnk.text.strip(),
                "name": cleaned_name,
                "suffix": suff_btn.text,
                "status": person.get('status', 'Present'),
                "attached_document": person.get('attached_document', '')
            }
            
            if is_edit:
                self.people[index] = new_data
            else:
                self.people.append(new_data)
                
            self.save_database()
            self.root.get_screen('main').refresh()
            popup.dismiss()

        save_btn.bind(on_release=save_action)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    # 📎 POPUP WINDOW FOR RECORD DOCUMENT ATTACHING AND SYSTEM VIEWING
    def document_manager_popup(self, index):
        person = self.people[index]
        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        doc_status_label = Label(
            text=f"Current Attachment: {person.get('attached_document', 'No Document Attached')}",
            size_hint_y=None, height=40, color=(0.12, 0.23, 0.35, 1), bold=True
        )
        content.add_widget(doc_status_label)
        
        initial_path = os.path.expanduser("~")
        if sys.platform != "win32" and os.path.exists("/media"):
            initial_path = "/media"
            
        filechooser = FileChooserIconView(
            filters=['*.jpg', '*.jpeg', '*.png', '*.pdf'], 
            path=initial_path,
            size_hint_y=0.7
        )
        content.add_widget(filechooser)
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        attach_btn = Button(text="📎 Attach File", bold=True, background_color=(0.18, 0.49, 0.73, 1))
        view_btn = Button(text="👁️ View", bold=True, background_color=(0.15, 0.68, 0.38, 1))
        print_btn = Button(text="🖨️ Print", bold=True, background_color=(0.12, 0.23, 0.35, 1))
        cancel_btn = Button(text="Close", bold=True)
        
        btn_layout.add_widget(attach_btn)
        btn_layout.add_widget(view_btn)
        btn_layout.add_widget(print_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title=f"Document Attachment Pipeline: {person['name']}", content=content, size_hint=(0.95, 0.85))
        
        def attach_action(instance):
            selected = filechooser.selection
            if selected:
                target_file_path = selected[0]
                filename = os.path.basename(target_file_path)
                local_destination = self.get_document_path(filename)
                
                try:
                    import shutil
                    shutil.copy2(target_file_path, local_destination)
                    self.people[index]['attached_document'] = filename
                    self.save_database()
                    doc_status_label.text = f"Current Attachment: {filename}"
                    self.root.get_screen('main').refresh()
                except Exception as e:
                    doc_status_label.text = f"Transfer Failed: {str(e)}"
            else:
                doc_status_label.text = "⚠️ Please click on a file from the picker grid below first!"

        def view_action(instance):
            filename = self.people[index].get('attached_document', '')
            if filename:
                full_path = self.get_document_path(filename)
                if os.path.exists(full_path):
                    try:
                        if sys.platform == "win32":
                            os.startfile(full_path)
                        elif sys.platform == "darwin":
                            subprocess.run(["open", full_path])
                        else:
                            subprocess.run(["xdg-open", full_path])
                    except Exception as e:
                        doc_status_label.text = f"Viewer error: {str(e)}"
                else:
                    doc_status_label.text = "⚠️ File storage mapping missing."
            else:
                doc_status_label.text = "⚠️ No file attached yet!"

        def print_action(instance):
            filename = self.people[index].get('attached_document', '')
            if filename:
                full_path = self.get_document_path(filename)
                self.print_image_file(full_path)
            else:
                doc_status_label.text = "⚠️ No file attached to print!"

        attach_btn.bind(on_release=attach_action)
        view_btn.bind(on_release=view_action)
        print_btn.bind(on_release=print_action)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    # 📥 EXCEL / CSV CONVERSION IMPORTERS AND EXPORTERS
    def import_excel_popup(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        filechooser = FileChooserIconView(filters=['*.csv'], path=os.getcwd())
        content.add_widget(filechooser)
        
        btn_layout = BoxLayout(size_hint_y=None, height=45, spacing=15)
        import_btn = Button(text="Import Selected Target CSV", bold=True, background_color=(0.18, 0.49, 0.73, 1))
        cancel_btn = Button(text="Cancel Operation")
        
        btn_layout.add_widget(import_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title="Select Target Source CSV Roster Database File", content=content, size_hint=(0.9, 0.8))
        
        def import_action(instance):
            if filechooser.selection:
                target_path = filechooser.selection[0]
                try:
                    with open(target_path, mode='r', encoding='utf-8-sig') as f:
                        reader = csv.DictReader(f)
                        new_records = []
                        for row in reader:
                            norm_row = {k.lower().strip(): v for k, v in row.items() if k}
                            name_val = norm_row.get('name', norm_row.get('full name', '')).strip()
                            if not name_val:
                                continue
                                
                            pref = norm_row.get('prefix', norm_row.get('rank', 'Rfn')).strip()
                            rnk = norm_row.get('rnk', norm_row.get('rank_desc', '')).strip()
                            suff = norm_row.get('suffix', norm_row.get('type', 'PE')).strip().upper()
                            stat = norm_row.get('status', norm_row.get('leave_type', 'Present')).strip()
                            doc = norm_row.get('attached_document', norm_row.get('doc', '')).strip()
                            
                            if pref not in self.ranks:
                                pref = "Rfn"
                            if suff not in ["PE", "MC", "CA"]:
                                suff = "PE"
                            if stat not in self.statuses:
                                stat = "Present"
                                
                            new_records.append({
                                "prefix": pref,
                                "rnk": rnk,
                                "name": name_val,
                                "suffix": suff,
                                "status": stat,
                                "attached_document": doc
                            })
                        
                        if new_records:
                            self.people.extend(new_records)
                            self.save_database()
                            self.root.get_screen('main').refresh()
                except Exception as e:
                    print(f"Failed CSV Data Extraction: {e}")
                popup.dismiss()

        import_btn.bind(on_release=import_action)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    def export_to_excel(self):
        export_filename = "exported_personnel_roster.csv"
        try:
            with open(export_filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["prefix", "rnk", "name", "suffix", "status", "attached_document"])
                for p in self.people:
                    writer.writerow([
                        p.get('prefix', 'Rfn'),
                        p.get('rnk', ''),
                        p.get('name', ''),
                        p.get('suffix', 'PE'),
                        p.get('status', 'Present'),
                        p.get('attached_document', '')
                    ])
            
            content = BoxLayout(orientation='vertical', padding=15, spacing=10)
            content.add_widget(Label(text=f"Roster exported successfully to:\n{os.path.abspath(export_filename)}", halign='center'))
            ok_btn = Button(text="Excellent", size_hint_y=None, height=40)
            content.add_widget(ok_btn)
            popup = Popup(title="CSV Export Complete Confirmation", content=content, size_hint=(0.8, 0.3))
            ok_btn.bind(on_release=popup.dismiss)
            popup.open()
        except Exception as e:
            print(f"Export execution failed: {e}")

    def confirm_clear_popup(self):
        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        content.add_widget(Label(text="Are you sure you want to completely wipe the personnel registry?", halign='center'))
        
        btn_layout = BoxLayout(size_hint_y=None, height=45, spacing=15)
        yes_btn = Button(text="Yes, Wipe Database", bold=True, background_color=(0.75, 0.22, 0.17, 1))
        no_btn = Button(text="Cancel", bold=True)
        
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title="CRITICAL WARNING: Database Destructive Action", content=content, size_hint=(0.8, 0.35))
        
        def wipe_action(instance):
            self.people = []
            self.save_database()
            self.root.get_screen('main').refresh()
            popup.dismiss()
            
        yes_btn.bind(on_release=wipe_action)
        no_btn.bind(on_release=popup.dismiss)
        popup.open()

    def print_action(self, text_content):
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_f:
                temp_f.write(text_content)
                temp_path = temp_f.name
            
            if sys.platform == "win32":
                os.startfile(temp_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", temp_path])
            else:
                subprocess.run(["xdg-open", temp_path])
        except Exception as e:
            print(f"Printing text report execution failed: {e}")

    def print_image_file(self, file_path):
        if not file_path or not os.path.exists(file_path):
            print("Print operation cancelled: Source target image file path is invalid.")
            return
            
        try:
            if sys.platform == "win32":
                os.startfile(file_path, "print")
            elif sys.platform == "darwin":
                subprocess.run(["lp", file_path], check=True)
            else:
                subprocess.run(["lp", file_path], check=True)
        except Exception as e:
            print(f"Printing image attachment tool failed: {e}")


# =========================================================================
# ⚙️ APPLICATION EXECUTION INSTANTIATION RUN BLOCK
# =========================================================================
if __name__ == '__main__':
    HRStrengthApp().run()

