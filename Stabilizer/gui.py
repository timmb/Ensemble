# -*- coding: utf-8 -*-

'''
This module contains code to hook up the GUI (generated using the Qt UI 
designer) to the rest of the code and any hand-written GUI code.
'''


import UX.MainWindow
from PySide import QtCore, QtGui
from PySide.QtGui import *
from PySide.QtCore import *
from pprint import pformat
from lib.texttable import Texttable
import json
import ast
from collections import namedtuple


def pr(x):
    print(x)
    return True

def assign(var, value):
    var = value

def assign_index(dictionary, name, new_value, log_function=None):
    if log_function: log_function('{} set to {}'.format(name, new_value, log_function))
    dictionary[name] = new_value

def try_assign_repr(dictionary, name, string_repr_of_new_value, log_function=None):
    try:
        dictionary[name] = ast.literal_eval(string_repr_of_new_value)
        if log_function: log_function('{} set to {}'.format(name, dictionary[name], log_function))
        return True
    except SyntaxError as e:
        return False


class MainWindow(QtGui.QMainWindow):

    sig_start_listening = QtCore.Signal()
    sig_stop_listening = QtCore.Signal()

    def __init__(self, stabilizer, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = UX.MainWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.stabilizer = stabilizer
        
        self.ui.saveSettingsButton.clicked.connect(self.ui.actionSaveSettings.trigger)
        self.ui.saveSettingsAsButton.clicked.connect(self.ui.actionSaveSettingsAs.trigger)
        self.ui.openSettingsButton.clicked.connect(self.ui.actionOpenSettings.trigger)
        self.ui.reloadSettingsButton.clicked.connect(self.ui.actionReloadSettings.trigger)
        self.ui.actionSaveSettings.triggered.connect(self.save_settings_action)
        self.ui.actionSaveSettingsAs.triggered.connect(self.save_settings_as_action)
        self.ui.actionOpenSettings.triggered.connect(self.open_settings_action)
        self.ui.actionReloadSettings.triggered.connect(self.reload_settings_action)

        self.ui.actionQuit.triggered.connect(stabilizer.quit)
        self.ui.logView.setModel(stabilizer.event_log)
        self.ui.enableInputCheckbox.setChecked(self.stabilizer.is_listening)
        self.ui.enableInputCheckbox.toggled.connect(self.start_or_stop_listening)
        self.ui.enableOutputCheckbox.setChecked(self.stabilizer.is_sending)
        self.ui.enableOutputCheckbox.toggled.connect(self.start_or_stop_sending)
        checkbox_variable_pairings = [
            (self.ui.calculateConvergenceCheckbox, self.stabilizer.convergence_manager.enable_calculate_convergence),
            (self.ui.logIncomingMessagesCheckbox, self.stabilizer.enable_log_incoming_messages),
            (self.ui.logOutgoingMessagesCheckbox, self.stabilizer.enable_log_outgoing_messages)
            ]
        for checkbox, var in checkbox_variable_pairings:
            checkbox.setChecked(var)
            checkbox.toggled.connect(lambda x: assign(var,x))
        self.create_dynamic_elements()
 
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(50)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start()

        # Signals emitted by this class
        self.sig_start_listening.connect(self.stabilizer.start_listening)
        self.sig_stop_listening.connect(self.stabilizer.stop_listening)

        self.show()

    def create_dynamic_elements(self):
        #create gui elements for settings in stabilizer dynamicall
        # todo: fix this - for some reason the lambda function isn't working
        # and it connects all spinboxes to change the same value
        # return
        self.settings_widgets = {}
        for var,val in self.stabilizer.settings.iteritems():
            page = self.ui.settingsPage
            layout = self.ui.formLayout
            if type(val)==float:
                label = QLabel(var, page)
                spinbox = QDoubleSpinBox(page)
                spinbox.setValue(val)
                spinbox.setSingleStep(0.001)
                spinbox.setDecimals(5)
                spinbox.setProperty('settingName', var)
                layout.setWidget(layout.rowCount(), layout.LabelRole, label)
                layout.setWidget(layout.rowCount()-1, layout.FieldRole, spinbox)
                spinbox.valueChanged[float].connect(self.set_setting_based_on_sender_property)
                self.settings_widgets[var] = spinbox
            # TODO: create widgets for other parameter types, including nested settings dictionaries

        # create Parameter widgets for the convergence manager parameters
        self.parameter_widgets = []
        self.ui.parametersArea.setLayout(QHBoxLayout())
        for name, param in self.stabilizer.convergence_manager.params.iteritems():
            p = ParameterWidget(
                name=name,
                parameter=param, 
                global_settings_dict=self.stabilizer.settings, 
                log_function=lambda x, name=name: self.stabilizer.log(x, module="Gui - "+name),
                parent=self)
            self.parameter_widgets.append(p)
            self.ui.parametersArea.layout().addWidget(p)

    def update_dynamic_elements(self):
        for var,val in self.stabilizer.settings.iteritems():
            self.settings_widgets[var].setValue(val)

    
    def set_setting_based_on_sender_property(self, newValue):
        setting = self.sender().property('settingName')
        self.stabilizer.settings[setting] = newValue
        self.stabilizer.log('Set {} to {}'.format(setting, newValue), 'Gui' )

    def update(self):
        '''Refresh gui based on self.stabilizer'''
        def update_text(text_edit, new_text):
            '''Prevents scroll bar from changing when updating'''
            scroll_bar_value = text_edit.verticalScrollBar().sliderPosition()
            text_edit.setPlainText(new_text)
            text_edit.verticalScrollBar().setSliderPosition(scroll_bar_value)
        update_text(self.ui.worldStateText, pformat(self.stabilizer.world_state))
        update_text(self.ui.convergedStateText, pformat(self.stabilizer.converged_state))
        update_text(self.ui.instrumentsText, pformat(self.stabilizer.instruments))
        update_text(self.ui.connectionsText, self.get_pretty_connections())
        update_text(self.ui.worldStateText, get_state_table(self.stabilizer.world_state))
        update_text(self.ui.convergedStateText, get_state_table(self.stabilizer.converged_state))
        # print 'narrative_speed', self.stabilizer.settings['narrative_speed']


    def start_or_stop_listening(self, start_listening=None):
        if start_listening==None:
            start_listening = not self.stabilizer.is_listening

        if start_listening:
            self.sig_start_listening.emit()
        else:
            self.sig_stop_listening.emit()

    def start_or_stop_sending(self, whether_to_start_sending):
        if whether_to_start_sending:
            self.stabilizer.start_sending()
        else:
            self.stabilizer.stop_sending()

    def get_pretty_connections(self):
        names = [name for name in self.stabilizer.instruments]
        if not names:
            return 'No instruments'
        names.sort()
        c = self.stabilizer.connections
        data = [[c.setdefault(ni, {}).get(nj,'') for ni in names] for nj in names]
        for i,row in enumerate(data):
            row.insert(0, names[i])
        header_row = ['']+names
        data.insert(0, header_row)

        table = Texttable()
        table.set_cols_align(['r']*(len(names)+1))
        table.add_rows(data)
        return table.draw() + '\nRaw data:\n'+pformat(c)

    def load_settings(self, json_filename):
        with open(json_filename, 'r') as f:
            try:
                self.stabilizer.settings = json.load(f)
                self.stabilizer.log('Settings loaded from '+json_filename, 'Gui')
            except Exception as e:
                self.stabilizer.log('Error loading settings from {}: {}: {}'.format(json_filename, type(e), e.message), "Gui")

    def save_settings(self, json_filename):
        with open(json_filename, 'w') as out:
            out.write(json.dumps(self.stabilizer.settings, indent=4))
            self.stabilizer.log('Settings written to '+json_filename, 'Gui')

    def open_settings_action(self):
        filename = QFileDialog.getOpenFileName(self, 'Open JSON Stabilizer settings', '', 'JSON files (*.json)', 'JSON files (*.json)')[0]
        if filename:
            self.load_settings(filename)
            self.update_dynamic_elements()
        self.ui.settingsFile.setText(filename)

    def reload_settings_action(self):
        filename = self.ui.settingsFile.text()
        if filename:
            self.load_settings(filename)
        else:
            self.stabilizer.log('Cannot reload file as no filename has been provided.', 'Gui')

    def save_settings_action(self):
        filename = self.ui.settingsFile.text()
        if filename:
            self.save_settings(filename)
        else:
            self.save_settings_as_action()

    def save_settings_as_action(self):
        filename = QFileDialog.getSaveFileName(self, 'Save JSON Stabilizer settings', '', 'JSON files (*.json)', 'JSON files (*.json)')[0]
        if filename:
            self.save_settings(filename)
            self.ui.settingsFile.setText(filename)



def get_state_table(state):
    ''' State is dict of: param -> instrument -> [value]
    '''
    if not state:
        return ''
    # def s(lst):
        # return ', '.join(('%0.2f' % x for x in lst))
    params = state.keys()
    insts = set()
    for param in params:
        for inst in state[param].keys():
            insts.add(inst)
    insts = list(insts)

    header_row = [' ']+insts
    data = [header_row]
    if len(data)==1:
        data.append(['']*len(data[0]))
    for param in params:
        row = [param]+[(state.get(param,{}).get(inst,[[]])) for inst in insts]
        data.append(row)
    table = Texttable()
    table.set_cols_align(['r']*(len(header_row)))
    table.add_rows(data)
    return table.draw()


class IgnoreScrollWheelEventFilter(QObject):
    '''This is a filter to prevent spin boxes from changing in response to scrolling.
    '''
    def eventFilter(self, object, event):
        if event.type() == QEvent.Wheel and not object.hasFocus():
            event.ignore()
            return True
        return object.eventFilter(object, event)



class ParameterWidget(QGroupBox):
    ignoreScrollWheelEventFilter = IgnoreScrollWheelEventFilter()

    def __init__(self, name, parameter, global_settings_dict, log_function=None, parent=None):
        QGroupBox.__init__(self, parent)
        self._name = name
        self._settings = global_settings_dict
        self._layout = QFormLayout(self)
        self._log_function = log_function
        self.setLayout(self._layout)
        # model defines the pairings between variables and widgets
        # all variables live inside a dictionary somewhere
        self._model = [
            # {dictionary, var_name, widget, widget_update_function, last_value}
        ]
        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.update)

        # self._layout.addRow(QLabel(name, self))
        self.setTitle(name)
        if type(parameter.manual_value) is list and map(type, parameter.manual_value) in ([float],[int]):
            self.add_indexed_element(
                parameter.manual_value, 
                0, 
                False, 
                parameter.set_manual_value,
                widget_label='Manual value',
                )
        else:
            self.add_indexed_element(
                parameter.__dict__, 
                'manual_value', 
                False, 
                parameter.set_manual_value, 
                widget_label='Manual value',
                )
        
        self.add_heading('State')
        for p in parameter.editable_values:
            self.add_indexed_element(parameter.__dict__, p, False)
        for p in parameter.readonly_values:
            self.add_indexed_element(parameter.__dict__, p, True)

        self.add_heading('Settings')
        for p in sorted(parameter._settings.iterkeys()):
            self.add_indexed_element(parameter._settings, p, False)


    def add_heading(self, title):
        label = QLabel(title, self)
        font = label.font()
        font.setBold(True)
        label.setFont(font)
        self._layout.addRow(label)
        self._layout.addRow(self.make_horizontal_line())


    def add_indexed_element(self, d, name, is_read_only, 
        update_function=None, widget_label=None):
        '''
        Creates a widget that sets the value indexed by `name` in dict/list `d`,
        adds these elements to self._model.
        Leave update_function as None for default.
        widget_label defaults to name
        '''
        # print 'name',self._name,'log function',self._log_function
        if ((type(d) is dict and name not in d)
                or (type(d) is list and name>=len(d))):
            print('ParameterWidget: Error indexing {} in {}'.format(name, d))
            assert(name in d)
        if type(d[name]) is float:
            widget = QDoubleSpinBox(self)
            widget.setSingleStep(0.01)
            widget.setValue(d[name])
            widget.valueChanged.connect(update_function 
                or (lambda x: assign_index(d, name, x, self._log_function))) # default arg
            widget_update_function = widget.setValue
        elif type(d[name]) is int:
            widget = QSpinBox(self)
            widget.setValue(d[name])
            widget.valueChanged.connect(update_function 
                or (lambda x: assign_index(d, name, x, self._log_function))) # default arg
            widget_update_function = widget.setValue
        else:
            widget = QLineEdit(self)
            widget.setText(repr(d[name]))
            widget.editingFinished.connect(
                update_function 
                and (lambda: update_function(widget.text()))
                or (lambda: try_assign_repr(d, name, widget.text(), self._log_function))) # default arg
            widget_update_function = widget.setText

        if is_read_only:
            widget.setReadOnly(True)
            widget.setEnabled(False)
        # widget.focusInEvent = lambda event: widget.setFocusPolicy(Qt.WheelFocus)
        # widget.focusOutEvent = lambda event: widget.setFocusPolicy(Qt.StrongFocus)
        widget.setFocusPolicy(Qt.StrongFocus)
        widget.installEventFilter(self.ignoreScrollWheelEventFilter)
        self._layout.addRow(widget_label or name, widget)
        self._model.append({
            'dictionary' : d, 
            'var_name' : name, 
            'widget' : widget, 
            'widget_update_function' : widget_update_function, 
            'last_value' : d[name],
            })

    def make_horizontal_line(self):
        line = QFrame(self);
        line.setGeometry(QRect(320, 150, 118, 3))
        line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    def update(self):
        try:
            for element in self._model:
                if element['dictionary']['var_name']!=element['prev_value']:
                    element['prev_value'] = element['dictionary']['var_name']
                    element['widget'].blockSignals(True)
                    element['widget_update_function'](element['prev_value'])
                    element['widget'].blockSignals(False)
        except Exceptions as e:
            import pdb; pdb.set_trace()



