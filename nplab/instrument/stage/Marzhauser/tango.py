"""Created January 2022
Author: James Stevenson
"""

from nplab.instrument import Instrument
from nplab.instrument.stage import Stage
from ctypes import c_int, c_double, c_bool, c_char_p, byref, POINTER, cdll
import sys
import os


class Tango(Stage):
    """Control object for Marzhauser Tango stages

    Originally written for a Tango 3 Desktop 3-axis stage. The Tango DLL looks
    valid for all Tango stages, so hopefully this class works for others too.
    """
    def __init__(self, unit='u'):
        Instrument.__init__(self)
        self.unit = unit

        # Connect to Tango
        lsid = c_int()
        return_value = tango_dll.LSX_CreateLSID(byref(lsid))
        assert return_value == 0, f'Tango.LSX_CreateLSID returned {return_value}'
        self.lsid = lsid.value
        self.ConnectSimple(-1, None, 57600, False)

        self.set_units(unit)

    def close(self):
        """Close Tango connection and perform necessary cleanup"""
        self.Disconnect()
        self.FreeLSID()

    def move(self, pos, axis, relative=False):
        """Move the stage along a single axis"""
        if axis not in self.axis_names:
            raise f'{axis} is not a valid axis, must be one of {self.axis_names}'
        axis_number = self.translate_axis(axis)
        if relative:
            self.MoveRelSingleAxis(axis_number, pos, True)
        else:
            self.MoveAbsSingleAxis(axis_number, pos, True)

    def get_position(self, axis=None):
        """Get current positions of all axes, or, optionally, a single axis"""
        if axis is None:
            return self.GetPos()
        return self.GetPosSingleAxis(axis)

    def is_moving(self, axes=None):
        """Returns True if any of the specified axes are in motion."""
        velocities = self.IsVel()
        for velocity in velocities.values():
            if velocity != 0:
                return True
        return False

    def set_units(self, unit):
        """Sets all dimensions to the desired unit"""
        unit_code = Tango.translate_unit(unit)
        self.SetDimensions(unit_code, unit_code, unit_code, unit_code)

    # ============== Wrapped DLL Functions ==============
    # The following functions directly correspond to Tango DLL functions
    # As much as possible, they should present Python-like interfaces:
    # 1) Accept and return Python variables, not ctype types
    # 2) Return values rather than set them to referenced variables
    # 3) Check for error codes and raise exceptions
    # Note: error codes and explanations are in the Tango DLL documentation
    def ConnectSimple(self, interface_type, com_name, baud_rate, show_protocol):
        """Wrapper for DLL function LSX_ConnectSimple"""
        #  com_name must be a bytes object, which we get by encoding as utf8
        if type(com_name) == str:
            com_name = com_name.encode('utf-8')
        try:
            return_value = tango_dll.LSX_ConnectSimple(c_int(self.lsid),
                                                       c_int(interface_type),
                                                       com_name,
                                                       c_int(baud_rate),
                                                       c_bool(show_protocol))
        except Exception as e:
            raise Exception(f'Tango.LSX_ConnectSimple raised exception: {str(e)}')
        if return_value == 4005:
            raise Exception('Tango DLL raised error 4005: "Error while ' \
                            'initializing interface." This can happen if ' \
                            'you specify the wrong port, or other software ' \
                            'is already be connected to the Tango.')
        else:
            assert return_value == 0, f'Tango.LSX_ConnectSimple returned {return_value}'

    def Disconnect(self):
        """Wrapper for DLL function LSX_Disconnect"""
        try:
            return_value = tango_dll.LSX_Disconnect(c_int(self.lsid))
        except Exception as e:
            raise Exception(f'Tango.LSX_Disconnect raised exception: {str(e)}')
        assert return_value == 0, f'Tango.LSX_Disconnect returned {return_value}'

    def FreeLSID(self):
        """Wrapper for DLL function LSX_FreeLSID"""
        try:
            return_value = tango_dll.LSX_FreeLSID(c_int(self.lsid))
        except Exception as e:
            raise Exception(f'Tango.LSX_FreeLSID raised exception: {str(e)}')
        assert return_value == 0, f'Tango.LSX_FreeLSID returned {return_value}'

    def SetDimensions(self, x_dim, y_dim, z_dim, a_dim):
        """Wrapper for DLL function LSX_SetDimensions"""
        try:
            return_value = tango_dll.LSX_SetDimensions(c_int(self.lsid),
                                                       c_int(x_dim),
                                                       c_int(y_dim),
                                                       c_int(z_dim),
                                                       c_int(a_dim))
        except Exception as e:
            raise Exception(f'Tango.LSX_SetDimensions raised exception: {str(e)}')
        assert return_value == 0, f'Tango.LSX_SetDimensions returned {return_value}'

    def MoveAbsSingleAxis(self, axis_number, value, wait):
        """Wrapper for DLL function LSX_MoveAbsSingleAxis"""
        try:
            return_value = tango_dll.LSX_MoveAbsSingleAxis(c_int(self.lsid),
                                                           c_int(axis_number),
                                                           c_double(value),
                                                           c_bool(wait))
        except Exception as e:
            raise Exception(f'Tango.LSX_MoveAbsSingleAxis raised exception: {str(e)}')
        assert return_value == 0, f'Tango.LSX_MoveAbsSingleAxis returned {return_value}'

    def MoveRelSingleAxis(self, axis_number, value, wait):
        """Wrapper for DLL function LSX_MoveRelSingleAxis"""
        try:
            return_value = tango_dll.LSX_MoveRelSingleAxis(c_int(self.lsid),
                                                           c_int(axis_number),
                                                           c_double(value),
                                                           c_bool(wait))
        except Exception as e:
            raise Exception(f'Tango.LSX_MoveRelSingleAxis raised exception: {str(e)}')
        assert return_value == 0, f'Tango.LSX_MoveRelSingleAxis returned {return_value}'

    def GetPos(self):
        """Wrapper for DLL function LSX_GetPos"""
        x_pos = c_double()
        y_pos = c_double()
        z_pos = c_double()
        a_pos = c_double()
        try:
            return_value = tango_dll.LSX_GetPos(c_int(self.lsid),
                                                byref(x_pos),
                                                byref(y_pos),
                                                byref(z_pos),
                                                byref(a_pos))
        except Exception as e:
            raise Exception(f'Tango.LSX_GetPos raised exception: {str(e)}')
        assert return_value == 0, f'Tango.LSX_GetPos returned {return_value}'
        return {'x': x_pos.value, 'y': y_pos.value,
                'z': z_pos.value, 'a': a_pos.value}

    def GetPosSingleAxis(self, axis_number):
        """Wrapper for DLL function LSX_GetPosSingleAxis"""
        pos = c_double()
        try:
            return_value = tango_dll.LSX_GetPosSingleAxis(c_int(self.lsid),
                                                          byref(pos))
        except Exception as e:
            raise Exception(f'Tango.LSX_GetPosSingleAxis raised exception: {str(e)}')
        assert return_value == 0, f'Tango.LSX_GetPosSingleAxis returned {return_value}'
        return pos.value

    def GetVel(self):
        """Wrapper for DLL function LSX_GetVel
        Returns axis velocities as they are set to move at, whether they are
        moving now or not.
        """
        x_velocity = c_double()
        y_velocity = c_double()
        z_velocity = c_double()
        a_velocity = c_double()
        try:
            return_value = tango_dll.LSX_GetVel(c_int(self.lsid),
                                                byref(x_velocity),
                                                byref(y_velocity),
                                                byref(z_velocity),
                                                byref(a_velocity))
        except Exception as e:
            raise Exception(f'Tango.LSX_GetVel raised exception: {str(e)}')
        assert return_value == 0, f'Tango.LSX_GetVel returned {return_value}'
        return {'x': x_velocity.value, 'y': y_velocity.value,
                'z': z_velocity.value, 'a': a_velocity.value}

    def IsVel(self):
        """Wrapper for DLL function LSX_IsVel
        Gets the actual velocities at which the axes are currently travelling.
        """
        x_velocity = c_double()
        y_velocity = c_double()
        z_velocity = c_double()
        a_velocity = c_double()
        try:
            return_value = tango_dll.LSX_IsVel(c_int(self.lsid),
                                               byref(x_velocity),
                                               byref(y_velocity),
                                               byref(z_velocity),
                                               byref(a_velocity))
        except Exception as e:
            raise Exception(f'Tango.LSX_IsVel raised exception: {str(e)}')
        assert return_value == 0, f'Tango.LSX_IsVel returned {return_value}'
        return {'x': x_velocity.value, 'y': y_velocity.value,
                'z': z_velocity.value, 'a': a_velocity.value}

    def SetVelSingleAxis(self, axis_number, velocity):
        """Wrapper for DLL function LSX_SetVelSingleAxis
        Set velocity a single axis is to move at, whether it is moving now or not.
        """
        try:
            return_value = tango_dll.LSX_SetVelSingleAxis(c_int(self.lsid),
                                                          c_int(axis_number),
                                                          c_double(velocity))
        except Exception as e:
            raise Exception(f'Tango.LSX_SetVelSingleAxis raised exception: {str(e)}')
        assert return_value == 0, f'Tango.LSX_SetVelSingleAxis returned {return_value}'

# =============================================================================
# ============================== Module functions =============================
# =============================================================================
def translate_unit(unit):
    """Translate English looking unit to unit code that Tango understands"""
    if unit == 'Microsteps':
        return 0
    elif unit == 'um':
        return 1
    elif unit == 'mm':
        return 2
    elif unit == 'degree':
        return 3
    elif unit == 'revolutions':
        return 4
    elif unit == 'cm':
        return 5
    elif unit == 'm':
        return 6
    elif unit == 'inch':
        return 7
    elif unit == 'mil':
        return 8
    else:
        raise Exception(f'Tried to put translate unknown unit: {unit}')


def translate_axis(axis):
    """Translate an axis (x, y, z, a) to axis-code that Tango understands"""
    if axis == 'x':
        return 1
    elif axis == 'y':
        return 2
    elif axis == 'z':
        return 3
    elif axis == 'a':
        return 4
    else:
        raise Exception(f'Tried to translate unknown axis: {axis}')


# =============================================================================
# ================================ DLL Import =================================
# =============================================================================
system_bits = '64' if (sys.maxsize > 2**32) else '32'
path_here = os.path.dirname(__file__)
tango_dll = cdll.LoadLibrary(f'{path_here}/DLL/{system_bits}/Tango_DLL.dll')

# Set arg types for all dll functions we call
# LSID: Used to tell the DLL which Tango we are sending a command to
# The DLL can have up to 8 simultaneously connected Tangos
tango_dll.LSX_CreateLSID.argtypes = [POINTER(c_int)]
tango_dll.LSX_ConnectSimple.argtypes = [c_int, c_int, c_char_p, c_int, c_bool]
tango_dll.LSX_Disconnect.argtypes = [c_int]
tango_dll.LSX_FreeLSID.argtypes = [c_int]
tango_dll.LSX_SetDimensions.argtypes = [c_int, c_int, c_int, c_int, c_int]
tango_dll.LSX_MoveRelSingleAxis.argtypes = [c_int, c_int, c_double, c_bool]
tango_dll.LSX_MoveAbsSingleAxis.argtypes = [c_int, c_int, c_double, c_bool]
tango_dll.LSX_GetPos.argtypes = [c_int, POINTER(c_double), POINTER(c_double),
                                 POINTER(c_double), POINTER(c_double)]
tango_dll.LSX_GetPosSingleAxis.argtypes = [c_int, c_int, POINTER(c_double)]
tango_dll.LSX_GetVel.argtypes = [c_int, POINTER(c_double), POINTER(c_double),
                                 POINTER(c_double), POINTER(c_double)]
tango_dll.LSX_IsVel.argtypes = [c_int, POINTER(c_double), POINTER(c_double),
                                POINTER(c_double), POINTER(c_double)]
tango_dll.LSX_SetVelSingleAxis.argtypes = [c_int, c_int, c_double]
