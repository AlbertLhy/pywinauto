# -*- coding: utf-8 -*-
# GUI Application automation and testing library
# Copyright (C) 2006-2019 Mark Mc Mahon and Contributors
# https://github.com/pywinauto/pywinauto/graphs/contributors
# http://pywinauto.readthedocs.io/en/latest/credits.html
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of pywinauto nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Tests for Linux AtspiWrapper"""

import os
import sys
import time
import mock
import unittest
import ctypes

if sys.platform.startswith("linux"):
    sys.path.append(".")
    from pywinauto.linux.atspi_objects import AtspiAccessible
    from pywinauto.linux.atspi_objects import AtspiImage
    from pywinauto.linux.atspi_objects import _AtspiRect
    from pywinauto.linux.atspi_objects import _AtspiPoint
    from pywinauto.linux.atspi_objects import _AtspiCoordType
    from pywinauto.linux.atspi_element_info import AtspiElementInfo
    from pywinauto.linux.application import Application
    from pywinauto.controls.atspiwrapper import AtspiWrapper
    from pywinauto.linux.atspi_objects import IATSPI
    from pywinauto.linux.atspi_objects import RECT
    from pywinauto.linux.atspi_objects import POINT
    from pywinauto.controls.atspi_controls import ImageWrapper

app_name = r"gtk_example.py"


def _test_app():
    test_folder = os.path.join(os.path.dirname
                               (os.path.dirname
                                (os.path.dirname
                                 (os.path.abspath(__file__)))),
                               r"apps/Gtk_samples")
    sys.path.append(test_folder)
    return os.path.join(test_folder, app_name)


def print_tree(start_el_info, level_shifter=""):
    if level_shifter == "":
        print(start_el_info.control_type, "  ", start_el_info.control_id, "!")
        level_shifter += "-"

    for children in start_el_info.children():
        print(level_shifter, "  ", children.control_type, "    ", children.control_id, children.runtime_id, "!")
        print_tree(children, level_shifter + "-")


if sys.platform.startswith("linux"):
    class AtspiWrapperTests(unittest.TestCase):

        """Unit tests for the AtspiWrapper class"""

        def setUp(self):
            self.desktop_info = AtspiElementInfo()
            self.desktop_wrapper = AtspiWrapper(self.desktop_info)
            self.app = Application()
            self.app.start(_test_app())
            self.app_wrapper = self.app.gtk_example.wrapper_object()
            self.app_frame = self.app.gtk_example.Frame

        def tearDown(self):
            self.app.kill()

        def test_set_window_focus(self):
            self.app_frame.set_focus()
            states = self.app_frame.get_states()
            self.assertIn("STATE_VISIBLE", states)
            self.assertIn("STATE_SHOWING", states)

        def test_top_level_parent_for_app_return_app(self):
            self.assertEqual(self.app_wrapper.top_level_parent().element_info.control_type, "Application")

        def test_top_level_parent_for_button_return_app(self):
            self.assertEqual(self.app_frame.Panel.top_level_parent().element_info.control_type,
                             "Application")

        def test_root_return_desktop(self):
            self.assertEqual(self.app_wrapper.root(), self.desktop_info)

        def test_class_name_return_element_info_class_name(self):
            self.assertEqual(self.app_wrapper.class_name(), "Application")

        def test_window_text(self):
            self.assertEqual(self.app_wrapper.window_text(), app_name)

        def test_control_id(self):
            self.assertEqual(self.app_wrapper.control_id(), IATSPI().known_control_types["Application"])

        def test_image(self):
            img_wrp = self.app_frame.Icon.wrapper_object()
            self.assertEqual(img_wrp.description(), u'')
            self.assertEqual(img_wrp.class_name(), u"Icon")
            self.assertEqual(img_wrp.locale(), u'')
            self.assertEqual(img_wrp.size(), (48, 24))
            pos = img_wrp.position()
            self.assertEqual(pos.x, 422)
            self.assertAlmostEqual(pos.y, 31, delta=2)
            bb = img_wrp.bounding_box()
            self.assertEqual(bb.left, pos.x)
            self.assertEqual(bb.top, pos.y)
            self.assertEqual(bb.right, 470)
            self.assertAlmostEqual(bb.bottom, 55, delta=2)

        def test_can_get_rectangle(self):
            rect = self.app_frame.Panel.rectangle()
            self.assertEqual(rect.width(), 600)
            rect = self.app_frame.Icon.rectangle()
            self.assertAlmostEqual(rect.height(), 26, delta=2)

        def test_can_get_process_id(self):
            self.assertEqual(self.app_wrapper.process_id(), self.app.process)

        def test_is_dialog_for_Application_is_true(self):
            self.assertTrue(self.app_wrapper.is_dialog())

        def test_is_dialog_for_button_is_false(self):
            self.assertFalse(self.app_frame.Panel.Click.is_dialog())

        def test_can_get_children(self):
            self.assertEqual(self.app_frame.control_id(), IATSPI().known_control_types["Frame"])

        def test_can_get_descendants(self):
            self.assertTrue(len(self.app_wrapper.descendants()) > len(self.app_wrapper.children()))

        def test_can_get_control_count(self):
            self.assertEqual(self.app_wrapper.control_count(), 1)

        def test_can_get_properties(self):
            props = self.app_wrapper.get_properties()
            self.assertEqual(props['class_name'], 'Application')
            self.assertEqual(props['friendly_class_name'], 'Application')
            self.assertEqual(props['control_id'], IATSPI().known_control_types["Application"])

        def test_app_is_child_of_desktop(self):
            self.assertTrue(self.app_wrapper.is_child(self.desktop_wrapper))

    class AtspiWrapperImageMockedTests(unittest.TestCase):

        """Mocked unit tests for atspi_controls.ImageWrapper.image property"""

        def setUp(self):
            self.info = AtspiElementInfo()
            self.patch_get_role = mock.patch.object(AtspiAccessible, 'get_role')
            self.mock_get_role = self.patch_get_role.start()
            self.mock_get_role.return_value = IATSPI().known_control_types["Image"]
            self.wrp = AtspiWrapper(self.info)

        def tearDown(self):
            self.patch_get_role.stop()

        def test_image_success(self):
            self.assertEqual(type(self.wrp), ImageWrapper)
            self.assertEqual(type(self.wrp.image), AtspiImage)

            # Icon role should be also handled by AtspiImage
            self.mock_get_role.return_value = IATSPI().known_control_types["Icon"]
            iconWrp = AtspiWrapper(self.info)
            self.assertEqual(type(iconWrp.image), AtspiImage)

        def test_image_fail_on_wrong_role(self):
            self.mock_get_role.return_value = IATSPI().known_control_types["Invalid"]
            self.wrp = AtspiWrapper(self.info)
            self.assertEqual(type(self.wrp), AtspiWrapper)
            self.assertRaises(AttributeError, lambda: self.wrp.image)

        @mock.patch.object(AtspiImage, '_get_image_locale')
        def test_image_get_locale_success(self, mock_get_locale):
            mock_get_locale.return_value = b"I"
            self.assertEqual(self.wrp.image.get_locale(), b"I")

        @mock.patch.object(AtspiImage, '_get_image_description')
        def test_image_get_description_success(self, mock_get_description):
            mock_get_description.return_value = b"descr"
            self.assertEqual(self.wrp.image.get_description(), b"descr")

        @mock.patch.object(AtspiImage, '_get_image_extents')
        def test_image_get_image_extents_success(self, mock_get_extents):
            extents_rect = _AtspiRect(22, 11, 33, 44)
            mock_get_extents.return_value = ctypes.pointer(extents_rect)
            self.assertEqual(self.wrp.image.get_extents(), RECT(extents_rect))
            self.assertEqual(mock_get_extents.call_args[0][1],
                             _AtspiCoordType.ATSPI_COORD_TYPE_WINDOW)

        @mock.patch.object(AtspiImage, '_get_image_position')
        def test_image_get_image_position_success(self, mock_get_position):
            pnt = _AtspiPoint()
            pnt.x = 55
            pnt.y = 66
            mock_get_position.return_value = ctypes.pointer(pnt)
            self.assertEqual(self.wrp.image.get_position(), POINT(pnt.x, pnt.y))
            self.assertEqual(mock_get_position.call_args[0][1],
                             _AtspiCoordType.ATSPI_COORD_TYPE_WINDOW)


if __name__ == "__main__":
    unittest.main()
