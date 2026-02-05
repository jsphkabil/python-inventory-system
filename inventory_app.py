"""
IT Help Room Inventory Tracker
A Python Tkinter application with SQLite database for tracking IT equipment.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import database as db


class InventoryApp:
    """Main application class for the IT Help Room Inventory Tracker."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("IT Help Room Inventory")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Initialize database
        db.init_database()
        
        # Store data
        self.locations = db.get_all_locations()
        self.selected_item_id: Optional[int] = None
        self.new_count_var = tk.StringVar(value="0")
        
        # Configure styles
        self.setup_styles()
        
        # Build UI
        self.build_ui()
        
        # Load initial data
        self.refresh_items()
        self.refresh_summary()
    
    def setup_styles(self):
        """Configure ttk styles for the application."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background='#f5f5f5')
        style.configure('TLabel', background='#f5f5f5', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10), padding=5)
        style.configure('Header.TLabel', font=('Segoe UI', 24, 'bold'), background='#f5f5f5')
        style.configure('Subheader.TLabel', font=('Segoe UI', 11), foreground='#666666', background='#f5f5f5')
        style.configure('Section.TLabel', font=('Segoe UI', 14, 'bold'), background='#ffffff')
        style.configure('ItemName.TLabel', font=('Segoe UI', 16, 'bold'), background='#ffffff')
        style.configure('Count.TLabel', font=('Segoe UI', 12), background='#ffffff')
        style.configure('Card.TFrame', background='#ffffff', relief='solid', borderwidth=1)
        
        # Configure Treeview
        style.configure('Treeview', font=('Segoe UI', 10), rowheight=40)
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
    
    def build_ui(self):
        """Build the main user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.build_header(main_frame)
        
        # Search and filter section
        self.build_search_section(main_frame)
        
        # Content area (items list + editor)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Items list (left side)
        self.build_items_list(content_frame)
        
        # Item editor (right side)
        self.build_item_editor(content_frame)
        
        # Summary section
        self.build_summary_section(main_frame)
    
    def build_header(self, parent: ttk.Frame):
        """Build the header section."""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            header_frame,
            text="IT Help Room Inventory",
            style='Header.TLabel'
        ).pack()
        
        ttk.Label(
            header_frame,
            text="Track and manage IT equipment across all locations",
            style='Subheader.TLabel'
        ).pack()
    
    def build_search_section(self, parent: ttk.Frame):
        """Build the search and filter section."""
        search_frame = ttk.Frame(parent, style='Card.TFrame', padding=15)
        search_frame.pack(fill=tk.X)
        
        # Search and filter row
        filter_frame = ttk.Frame(search_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        filter_frame.columnconfigure(0, weight=1)
        filter_frame.columnconfigure(1, weight=1)
        
        # Search entry
        search_col = ttk.Frame(filter_frame)
        search_col.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        
        ttk.Label(search_col, text="Search Items", background='#ffffff').pack(anchor='w')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.refresh_items())
        search_entry = ttk.Entry(search_col, textvariable=self.search_var, width=40)
        search_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Location filter
        location_col = ttk.Frame(filter_frame)
        location_col.grid(row=0, column=1, sticky='ew', padx=(10, 0))
        
        ttk.Label(location_col, text="Filter by Location", background='#ffffff').pack(anchor='w')
        self.location_var = tk.StringVar(value='all')
        location_combo = ttk.Combobox(
            location_col,
            textvariable=self.location_var,
            state='readonly',
            width=30
        )
        location_combo['values'] = ['All Locations'] + [loc['name'] for loc in self.locations]
        location_combo.current(0)
        location_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_items())
        location_combo.pack(fill=tk.X, pady=(5, 0))
        
        # Action buttons row
        button_frame = ttk.Frame(search_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Add New Item",
            command=self.show_add_item_dialog
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Deploy Computer",
            command=self.show_deploy_dialog
        ).pack(side=tk.RIGHT)
    
    def build_items_list(self, parent: ttk.Frame):
        """Build the items list section."""
        list_frame = ttk.Frame(parent, style='Card.TFrame', padding=15)
        list_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        ttk.Label(
            list_frame,
            text="📦 Available Items",
            style='Section.TLabel'
        ).pack(anchor='w', pady=(0, 10))
        
        # Treeview for items
        columns = ('name', 'count', 'location')
        self.items_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            selectmode='browse'
        )
        
        self.items_tree.heading('name', text='Item Name')
        self.items_tree.heading('count', text='Count')
        self.items_tree.heading('location', text='Location')
        
        self.items_tree.column('name', width=200)
        self.items_tree.column('count', width=80, anchor='center')
        self.items_tree.column('location', width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.items_tree.bind('<<TreeviewSelect>>', self.on_item_select)
    
    def build_item_editor(self, parent: ttk.Frame):
        """Build the item editor section."""
        self.editor_frame = ttk.Frame(parent, style='Card.TFrame', padding=20)
        self.editor_frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
        
        # Placeholder when no item selected
        self.placeholder_frame = ttk.Frame(self.editor_frame)
        self.placeholder_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            self.placeholder_frame,
            text="📦",
            font=('Segoe UI', 48),
            background='#ffffff'
        ).pack(pady=(50, 10))
        
        ttk.Label(
            self.placeholder_frame,
            text="No Item Selected",
            style='Section.TLabel'
        ).pack()
        
        ttk.Label(
            self.placeholder_frame,
            text="Select an item from the list to update its inventory count",
            background='#ffffff',
            foreground='#666666'
        ).pack(pady=(5, 0))
        
        # Editor controls (hidden initially)
        self.controls_frame = ttk.Frame(self.editor_frame)
        
        # Item name and current count
        self.item_name_label = ttk.Label(
            self.controls_frame,
            text="Item Name",
            style='ItemName.TLabel'
        )
        self.item_name_label.pack(anchor='w')
        
        self.current_count_label = ttk.Label(
            self.controls_frame,
            text="Current Count: 0",
            style='Count.TLabel',
            foreground='#666666'
        )
        self.current_count_label.pack(anchor='w', pady=(5, 20))
        
        # Plus/Minus buttons
        buttons_frame = ttk.Frame(self.controls_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.minus_btn = ttk.Button(
            buttons_frame,
            text="  −  ",
            command=self.decrement_count,
            width=15
        )
        self.minus_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        self.plus_btn = ttk.Button(
            buttons_frame,
            text="  +  ",
            command=self.increment_count,
            width=15
        )
        self.plus_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
        
        # New count input
        new_count_frame = ttk.Frame(self.controls_frame)
        new_count_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            new_count_frame,
            text="New Count:",
            background='#ffffff',
            font=('Segoe UI', 11)
        ).pack(side=tk.LEFT)
        
        self.new_count_entry = ttk.Entry(
            new_count_frame,
            textvariable=self.new_count_var,
            width=10,
            font=('Segoe UI', 14),
            justify='center'
        )
        self.new_count_entry.pack(side=tk.RIGHT)
        
        # Validate input to only allow numbers
        vcmd = (self.root.register(self.validate_number), '%P')
        self.new_count_entry.configure(validate='key', validatecommand=vcmd)
        
        # Update and Delete buttons
        action_frame = ttk.Frame(self.controls_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.delete_btn = ttk.Button(
            action_frame,
            text="Delete Item",
            command=self.delete_selected_item
        )
        self.delete_btn.pack(side=tk.LEFT)
        
        self.update_btn = ttk.Button(
            action_frame,
            text="Update Count",
            command=self.update_item_count
        )
        self.update_btn.pack(side=tk.RIGHT)
    
    def build_summary_section(self, parent: ttk.Frame):
        """Build the inventory summary section."""
        summary_frame = ttk.Frame(parent, style='Card.TFrame', padding=15)
        summary_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(
            summary_frame,
            text="Inventory Summary",
            style='Section.TLabel'
        ).pack(anchor='w', pady=(0, 10))
        
        self.summary_container = ttk.Frame(summary_frame)
        self.summary_container.pack(fill=tk.X)
    
    def refresh_summary(self):
        """Refresh the inventory summary display."""
        # Clear existing summary widgets
        for widget in self.summary_container.winfo_children():
            widget.destroy()
        
        summary = db.get_location_summary()
        
        for i, loc in enumerate(summary):
            loc_frame = ttk.Frame(self.summary_container, padding=10)
            loc_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            
            ttk.Label(
                loc_frame,
                text=str(loc['total_count']),
                font=('Segoe UI', 20, 'bold'),
                background='#ffffff'
            ).pack()
            
            ttk.Label(
                loc_frame,
                text=loc['name'],
                background='#ffffff',
                foreground='#666666'
            ).pack()
            
            ttk.Label(
                loc_frame,
                text=f"{loc['item_count']} items",
                background='#ffffff',
                foreground='#999999',
                font=('Segoe UI', 9)
            ).pack()
    
    def refresh_items(self):
        """Refresh the items list based on current filters."""
        # Get filter values
        search = self.search_var.get()
        location_name = self.location_var.get()
        
        # Map location name to ID
        location_id = 'all'
        if location_name != 'All Locations':
            for loc in self.locations:
                if loc['name'] == location_name:
                    location_id = loc['id']
                    break
        
        # Clear current items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        # Load filtered items
        items = db.get_all_items(location_id, search)
        
        for item in items:
            self.items_tree.insert(
                '',
                tk.END,
                iid=str(item['id']),
                values=(item['name'], item['count'], item['location_name'])
            )
    
    def on_item_select(self, event):
        """Handle item selection in the treeview."""
        selection = self.items_tree.selection()
        
        if selection:
            item_id = int(selection[0])
            item = db.get_item_by_id(item_id)
            
            if item:
                self.selected_item_id = item_id
                self.show_editor(item)
        else:
            self.hide_editor()
    
    def show_editor(self, item: dict):
        """Show the item editor with the selected item's data."""
        self.placeholder_frame.pack_forget()
        self.controls_frame.pack(fill=tk.BOTH, expand=True)
        
        self.item_name_label.configure(text=item['name'])
        self.current_count_label.configure(text=f"Current Count: {item['count']}")
        self.new_count_var.set(str(item['count']))
    
    def hide_editor(self):
        """Hide the item editor and show the placeholder."""
        self.selected_item_id = None
        self.controls_frame.pack_forget()
        self.placeholder_frame.pack(fill=tk.BOTH, expand=True)
    
    def validate_number(self, value: str) -> bool:
        """Validate that input is a valid number."""
        if value == "":
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    def increment_count(self):
        """Increment the new count by 1."""
        try:
            current = int(self.new_count_var.get() or "0")
            self.new_count_var.set(str(current + 1))
        except ValueError:
            self.new_count_var.set("1")
    
    def decrement_count(self):
        """Decrement the new count by 1 (minimum 0)."""
        try:
            current = int(self.new_count_var.get() or "0")
            self.new_count_var.set(str(max(0, current - 1)))
        except ValueError:
            self.new_count_var.set("0")
    
    def update_item_count(self):
        """Update the selected item's count in the database."""
        if self.selected_item_id is None:
            return
        
        try:
            new_count = int(self.new_count_var.get() or "0")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
            return
        
        db.update_item_count(self.selected_item_id, new_count)
        
        # Refresh displays
        self.refresh_items()
        self.refresh_summary()
        
        # Update the editor display
        item = db.get_item_by_id(self.selected_item_id)
        if item:
            self.current_count_label.configure(text=f"Current Count: {item['count']}")
        
        # Re-select the item in the tree
        self.items_tree.selection_set(str(self.selected_item_id))
        
        messagebox.showinfo("Success", "Item count updated successfully!")
    
    def delete_selected_item(self):
        """Delete the currently selected item."""
        if self.selected_item_id is None:
            return
        
        item = db.get_item_by_id(self.selected_item_id)
        if not item:
            return
        
        result = messagebox.askyesno(
            "Delete Item?",
            f'Are you sure you want to delete "{item["name"]}" from the inventory?\n\nThis action cannot be undone.'
        )
        
        if result:
            db.delete_item(self.selected_item_id)
            self.hide_editor()
            self.refresh_items()
            self.refresh_summary()
            messagebox.showinfo("Success", f'"{item["name"]}" has been removed from inventory.')
    
    def show_add_item_dialog(self):
        """Show the dialog for adding a new item."""
        dialog = AddItemDialog(self.root, self.locations)
        self.root.wait_window(dialog.top)
        
        if dialog.result:
            name, count, location_id = dialog.result
            db.add_item(name, count, location_id)
            self.refresh_items()
            self.refresh_summary()
            messagebox.showinfo("Success", f'Added "{name}" to inventory. Yay I made a change!!')
    
    def show_deploy_dialog(self):
        """Show the dialog for deploying a computer."""
        items = db.get_all_items()
        dialog = DeployComputerDialog(self.root, items)
        self.root.wait_window(dialog.top)
        
        if dialog.result:
            db.deploy_items(dialog.result)
            self.refresh_items()
            self.refresh_summary()
            
            total_qty = sum(qty for _, qty in dialog.result)
            messagebox.showinfo("Success", f"Computer deployed with {total_qty} items!")


class AddItemDialog:
    """Dialog for adding a new inventory item."""
    
    def __init__(self, parent: tk.Tk, locations: list[dict]):
        self.result = None
        self.locations = locations
        
        self.top = tk.Toplevel(parent)
        self.top.title("Add New Item")
        self.top.geometry("400x270")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()
        
        # Center the dialog
        self.top.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 250) // 2
        self.top.geometry(f"+{x}+{y}")
        
        self.build_ui()
    
    def build_ui(self):
        """Build the dialog UI."""
        frame = ttk.Frame(self.top, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Item name
        ttk.Label(frame, text="Item Name:").pack(anchor='w')
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var, width=40).pack(fill=tk.X, pady=(5, 15))
        
        # Initial count
        ttk.Label(frame, text="Initial Count:").pack(anchor='w')
        self.count_var = tk.StringVar(value="0")
        ttk.Entry(frame, textvariable=self.count_var, width=40).pack(fill=tk.X, pady=(5, 15))
        
        # Location
        ttk.Label(frame, text="Location:").pack(anchor='w')
        self.location_var = tk.StringVar()
        location_combo = ttk.Combobox(
            frame,
            textvariable=self.location_var,
            state='readonly',
            width=37
        )
        location_combo['values'] = [loc['name'] for loc in self.locations]
        if self.locations:
            location_combo.current(0)
        location_combo.pack(fill=tk.X, pady=(5, 20))
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Cancel", command=self.top.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Add Item", command=self.submit).pack(side=tk.RIGHT)
    
    def submit(self):
        """Validate and submit the form."""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter an item name", parent=self.top)
            return
        
        try:
            count = int(self.count_var.get() or "0")
            if count < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid count (0 or greater)", parent=self.top)
            return
        
        location_name = self.location_var.get()
        location_id = None
        for loc in self.locations:
            if loc['name'] == location_name:
                location_id = loc['id']
                break
        
        if not location_id:
            messagebox.showerror("Error", "Please select a location", parent=self.top)
            return
        
        self.result = (name, count, location_id)
        self.top.destroy()


class DeployComputerDialog:
    """Dialog for deploying a computer (subtracting multiple items)."""
    
    def __init__(self, parent: tk.Tk, items: list[dict]):
        self.result = None
        self.items = items
        self.quantity_vars: dict[int, tk.StringVar] = {}
        
        self.top = tk.Toplevel(parent)
        self.top.title("Deploy Computer")
        self.top.geometry("700x500")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()
        
        # Center the dialog
        self.top.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 500) // 2
        self.top.geometry(f"+{x}+{y}")
        
        self.build_ui()

    ### Function for shopping-cart style 'Deploy Computer' window.
    def increment_count(self, var: tk.StringVar):
        """Increment the new count by 1."""
        try:
            current = int(var.get() or "0")
            var.set(str(current + 1))
        except ValueError:
            var.set("1")
    
    def decrement_count(self, var: tk.StringVar):
        """Decrement the new count by 1 (minimum 0)."""
        try:
            current = int(var.get() or "0")
            var.set(str(max(0, current - 1)))
        except ValueError:
            var.set("0")
    
    def build_ui(self):
        """Build the dialog UI."""
        frame = ttk.Frame(self.top, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            frame,
            text="Select items and quantities to deploy:",
            font=('Segoe UI', 11, 'bold')
        ).pack(anchor='w', pady=(0, 15))
        
        # Scrollable frame for items
        canvas = tk.Canvas(frame, height=350)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add items with quantity inputs
        for item in self.items:
            item_frame = ttk.Frame(scrollable_frame)
            item_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(
                item_frame,
                text=f"{item['name']} (Available: {item['count']})",
                width=40
            ).pack(side=tk.LEFT)
            
            qty_var = tk.StringVar(value="0")
            self.quantity_vars[item['id']] = qty_var
            
            ### +/- buttons for 'Deploy Computer' window.
            ttk.Button(
                item_frame,
                text="-",
                command=lambda v=qty_var: self.decrement_count(v),
                width=2,
                padding=(2, 1)
            ).pack(side=tk.LEFT, padx=(0, 5), pady=(4, 4))

            ttk.Button(
                item_frame,
                text="+",
                command=lambda v=qty_var: self.increment_count(v),
                width=2,
                padding=(2, 1)
            ).pack(side=tk.RIGHT, padx=(5, 0), pady=(4, 4))

            ttk.Entry(
                item_frame,
                textvariable=qty_var,
                width=4,
                justify='center'
            ).pack(side=tk.RIGHT)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(btn_frame, text="Cancel", command=self.top.destroy).pack(side=tk.RIGHT, padx=(5, 5))
        ttk.Button(btn_frame, text="Deploy", command=self.submit).pack(side=tk.RIGHT, padx=(5, 0))
    
    def submit(self):
        """Validate and submit the deployment."""
        deployments = []
        
        for item_id, qty_var in self.quantity_vars.items():
            try:
                qty = int(qty_var.get() or "0")
                if qty > 0:
                    # Find the item to check available quantity
                    item = next((i for i in self.items if i['id'] == item_id), None)
                    if item and qty > item['count']:
                        messagebox.showerror(
                            "Error",
                            f"Cannot deploy {qty} of '{item['name']}'. Only {item['count']} available.",
                            parent=self.top
                        )
                        return
                    deployments.append((item_id, qty))
            except ValueError:
                pass
        
        if not deployments:
            messagebox.showerror("Error", "Please select at least one item to deploy", parent=self.top)
            return
        
        self.result = deployments
        self.top.destroy()


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()


