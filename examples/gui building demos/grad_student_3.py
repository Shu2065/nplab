# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 18:08:38 2021

@author: Eoin
"""
from nplab.instrument import Instrument
from nplab.utils.notified_property import (DumbNotifiedProperty,
                                           NotifiedProperty)


class GradStudent(Instrument):
    angry = DumbNotifiedProperty(False) 
    catchphrase = DumbNotifiedProperty("This is fine") 
    
    def __init__(self):
        super().__init__()
        self._logger.info(f'Initializing {self.__class__}')
        self._beers = 0
        
    def get_beers(self):
        print(f"I've had {self._beers} beers")
        return self._beers
    
    def set_beers(self, new_value):
        if new_value > self._beers:
            print(f'drinking {new_value - self._beers} more beers')
        if new_value < self._beers:
            print(f'drinking {self._beers - new_value} coffees')
        self._beers = new_value
        
    beers = NotifiedProperty(get_beers, set_beers) 
    
    def speak(self):
        if self.angry:
            print(self.catchphrase.upper()) # upper case 
        else:
            print(self.catchphrase) 
        print(self._beers*'hic...  ')
        
    def get_qt_ui(self):
        return GradStudentUI(self) 
    
from nplab.ui.ui_tools import QuickControlBox  # ##


class GradStudentUI(QuickControlBox): ###
    def __init__(self, student):
        super().__init__()
        self.student = student
        
        self.add_checkbox('angry') # name of the variable to control
        self.add_lineedit('catchphrase')
        self.add_spinbox('beers') # or property
        self.add_button('speak') # or function to connect
        
        self.auto_connect_by_name(controlled_object=student)
    
if __name__ == '__main__':
    student = GradStudent()
    gui = student.show_gui(blocking=False)