# -*- coding: utf-8 -*-

__all__ = ['CategoriesDialog']

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from lib.actions import Actions
from lib import common
from lib import i18n
from lib.utils import create_pixbuf
from lib.utils import Message
from gui.widgets.viewcategory import ViewCategory
from db.categoriestable import CategoriesTable

class CategoriesDialog(gtk.Dialog):
    """
    Class used to generate dialog to allow user to enter/edit categories.
    """
    def __init__(self, parent=None, new=False):
        gtk.Dialog.__init__(self, title=_("Categories Manager"),
                            parent=parent, flags=gtk.DIALOG_MODAL)

        self.closebutton = self.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
        self.okbutton = self.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        self.set_icon_from_file(common.APP_ICON)

        self.new = new

        if parent:
            self.set_transient_for(parent)
            self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)

        self.currentrecord = {}

        # Set up the UI
        self._initialize_dialog_widgets()
        self._connect_fields()
        #self._populate_fields()
        self.actions = Actions()
        self._populateTreeView(self.actions.get_categories("id > 0 ORDER BY categoryname ASC"))

        if new:
            self._on_newbutton_clicked(None)
            self.topcontainer.get_label_widget().set_markup("<b>%s</b>" \
                                                     % _("New Category"))
            self.okbutton.set_label(gtk.STOCK_SAVE)
            self.closebutton.set_label(gtk.STOCK_CANCEL)

        else:
            index = parent.category.get_active()-2
            if index >= 0:
                self.list.set_cursor((index,))

    def _initialize_dialog_widgets(self):
        self.vbox.set_spacing(8)
        self.topcontainer = gtk.Frame("<b>%s</b>" % _("Categories"))
        self.topcontainer.props.label_widget.set_use_markup(True)
        self.topcontainer.set_shadow_type(gtk.SHADOW_NONE)
        self.topcontainer_alignment = gtk.Alignment()
        self.topcontainer_alignment.set_padding(10, 0, 12, 0)
        self.topcontainer.add(self.topcontainer_alignment)
        self.fieldbox = gtk.VBox(homogeneous=False, spacing=6)

        self.list = ViewCategory()
        self.list.set_size_request(300, 150)

        # ScrolledWindow
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.set_shadow_type(gtk.SHADOW_OUT)
        self.scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC,
                                       gtk.POLICY_AUTOMATIC)
        self.scrolledwindow.add(self.list)

        self.table = gtk.Table(rows=2, columns=2, homogeneous=False)
        self.table.set_col_spacing(0, 6)
        self.table.set_row_spacing(0, 6)

        self.namelabel = gtk.Label()
        self.namelabel.set_markup("%s " % _("Name:"))
        self.namelabel.set_alignment(0.00, 0.50)
        self.colorlabel = gtk.Label()
        self.colorlabel.set_markup("%s " % _("Color:"))
        self.colorlabel.set_alignment(0.00, 0.50)

        self.name_ = gtk.Entry()
        self.color = gtk.ColorButton()

        self.table.attach(self.namelabel, 0, 1, 0, 1, gtk.FILL, gtk.FILL)
        self.table.attach(self.colorlabel, 0, 1, 1, 2, gtk.FILL, gtk.FILL)
        self.table.attach(self.name_, 1, 2, 0, 1)
        self.table.attach(self.color, 1, 2, 1, 2)

        self.actionspack = gtk.HButtonBox()
        self.actionspack.set_layout(gtk.BUTTONBOX_END)
        self.actionspack.set_spacing(6)

        self.newbutton = gtk.Button(stock=gtk.STOCK_NEW)
        self.savebutton = gtk.Button(stock=gtk.STOCK_SAVE)
        self.deletebutton = gtk.Button(stock=gtk.STOCK_DELETE)

        self.actionspack.pack_start(self.newbutton)
        self.actionspack.pack_start(self.savebutton)
        self.actionspack.pack_start(self.deletebutton)

        if not self.new:
            self.fieldbox.pack_start(self.scrolledwindow,
                                     expand=True, fill=True)
        self.fieldbox.pack_start(self.table,
                                 expand=False, fill=True)
        if not self.new:
            self.fieldbox.pack_start(self.actionspack,
                                     expand=False, fill=True)
        self.topcontainer_alignment.add(self.fieldbox)
        self.vbox.pack_start(self.topcontainer,
                             expand=True, fill=True, padding=10)

        # Show all widgets
        self.show_all()

    def _connect_fields(self):
        self.list.connect('cursor_changed', self._on_list_cursor_changed)
        self.name_.connect("changed", self._on_edit)
        self.color.connect("color-set", self._on_edit)
        self.newbutton.connect("clicked", self._on_newbutton_clicked)
        self.savebutton.connect("clicked", self._on_savebutton_clicked)
        self.deletebutton.connect("clicked", self._on_deletebutton_clicked)

    def _populateTreeView(self, records):
        """ Populates the treeview control with the records passed """
        # Loops through bills collection
        path = 0
        found = 0

        for rec in records:
            self.list.add(self._formated_row(rec))
            if rec['categoryname'] == self.currentrecord.get('categoryname', ''):
                found = path
            path += 1

        self.list.set_cursor(found)

        return

    def _formated_row(self, row):
        """ Formats a bill to be displayed as a row. """
        # Make sure the row is created using fields in proper order
        fields = CategoriesTable.Fields
        # Initial list
        formated = []
        # Loop through 'fields' and color code them
        for key in fields:
            if key == 'color':
                color = gtk.gdk.color_parse(row['color'])
                red = color.red * 255 / 65535
                green = color.green * 255 / 65535
                blue = color.blue * 255 / 65535
                rgb = (red, green, blue)
                formated.append(create_pixbuf(rgb=rgb))
            else:
                formated.append(row[key])
        formated.append(row['color'])
        return formated

    def _on_list_cursor_changed(self, widget):
        # Get currently selected bill
        self._get_selected_record()
        # Update statusbar
        self._update_fields()
        self.deletebutton.set_sensitive(True)
        self.savebutton.set_sensitive(False)

    def _get_selected_record(self):
        """ Keeps track of the currently selected record """
        if len(self.list.listStore) > 0:
            selection = self.list.get_selection()
            _model, iteration = selection.get_selected()
            # The ID for the selected record
            category_id = _model.get_value(iteration, 0)
            # Now fetch it from the database
            self.currentrecord = self.actions.get_categories({'id': category_id})[0]
        else:
            self.currentrecord = {}

    def _update_fields(self):
        if not self.currentrecord:
            self.name_.set_text("")
            self.color.set_color(gtk.gdk.color_parse("#000"))
            return
        self.name_.set_text(self.currentrecord['categoryname'])
        try:
            color = gtk.gdk.color_parse(self.currentrecord['color'])
        except ValueError:
            color = gtk.gdk.color_parse("#000")
        self.color.set_color(color)

    def reloadTreeView(self, *arg):
        # Update list with updated record
        self.list.listStore.clear()
        self._populateTreeView(self.actions.get_categories(""))

    def _on_newbutton_clicked(self, button):
        self.currentrecord = {}
        self.name_.set_text("")
        self.color.set_color(gtk.gdk.color_parse("#000"))
        self.deletebutton.set_sensitive(False)
        self.savebutton.set_sensitive(False)
        self.name_.grab_focus()

    def _on_savebutton_clicked(self, button):
        # Extract input data
        name =  self.name_.get_text()
        color = self.color.get_color().to_string()

        # Check if it already exists
        rec = self.actions.get_categories("UPPER(categoryname) = '%s'" % name.upper())
        if rec:
            message = Message()
            message.ShowError(_("The category %s already exists in the database!") % name, self)
            return

        # We're updating an existing category.
        if self.currentrecord:
            id = self.currentrecord['id']
            row = self.actions.edit_category({'id': id,
                'categoryname': name,
                'color': color})
        # We're adding a new category.
        else:
            row = self.actions.add_category({'categoryname': name,
                'color': color})
            # Update our local "copy" directly from database
            self.currentrecord = self.actions.get_categories({'categoryname': name})[0]

        # Repopulate the grid
        self.reloadTreeView()

    def _on_deletebutton_clicked(self, button):
        if self.currentrecord:
            id = self.currentrecord['id']
            more = self.actions.get_bills({'catId': id})
            if len(more) > 1:
                message = Message()
                confirm = message.ShowQuestionYesNo("%s%s" % (
                    _("Do you really want to delete this category?\n") ,
                    ngettext("There is %d more bill in this category.",
                        "There are %d more bills in this category.",
                        (len(more) - 1)) % (len(more) - 1)), 
                    parentWindow=self, title=_("Confirmation"))
                if not confirm:
                    return
            row = self.actions.delete_category(int(id))
            self.currentrecord = {}
            self.name_.set_text("")
            self.color.set_color(gtk.gdk.color_parse("#000"))
            self.savebutton.set_sensitive(False)
            self.reloadTreeView()

    def _on_edit(self, widget):
        self.savebutton.set_sensitive(True)
