# !python
#
# Copyright 2021
# Authors: Mahdi Torkashvand

"""
lambda GUI.

Usage:
    app.py                              [options]

Options:
    -h --help                           Show this help.
    --client_port=PORT                  [default: 5002]
    --saving_mode=mode                  [default: 0]
    --zyla_camera_trigger_mode=mode     [default: 2]
    --format=format                     [default: UINT16_ZYX_25_512_512]
    --flir_exposure=exposure            [default: 25000]
    --zyla_camera=number                [default: *]
"""

import os
import json
import time
import tkinter
import tkinter.messagebox

from docopt import docopt

import lambda_scope
from lambda_scope.devices.app_client import Client
from lambda_scope.devices.utils import array_props_from_string

class LambdaApp():
    def __init__(self,
                 client_port,
                 saving_mode,
                 zyla_camera_trigger_mode,
                 fmt,
                 flir_exposure,
                 zyla_camera):

        self.client = Client(client_port)
        self.window = tkinter.Tk()

        self.window_width= self.window.winfo_screenwidth()
        self.window_height= self.window.winfo_screenheight()
        self.x_spacing = 5
        self.y_spacing = 8
        self.window.geometry("{}x{}".format(self.window_width, self.window_height))
        self.window.title("LAMBDA")
        self.mode_filename = os.path.join(os.path.dirname(lambda_scope.__file__),
                                          "modes", "imaging_modes.json")
        self.microfluidic_mode_filename = os.path.join(os.path.dirname(lambda_scope.__file__),
                                                       "modes", "microfluidic_modes.json")

        (_, _, shape) = array_props_from_string(fmt)

        self.gui_mode = {}
        self.lambda_mode = {}

        self.cam_num: int
        if zyla_camera == "*":
            self.cam_num = 1
        else:
            self.cam_num = int(zyla_camera)

        self.lambda_mode["top_microscope_saving_mode"] = saving_mode
        self.lambda_mode["bot_microscope_saving_mode"] = saving_mode
        self.lambda_mode["zyla_camera_trigger_mode"] = zyla_camera_trigger_mode
        self.lambda_mode["dragonfly_imaging_mode"] = 1
        self.lambda_mode["top_microscope_data_shape"] = [shape[0], shape[1], shape[2]]
        self.lambda_mode["z_resolution_in_um"] = 1
        self.lambda_mode["zyla_camera_exposure_time_in_ms"] = 10
        self.lambda_mode["laser_power"] = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.lambda_mode["laser_output_repeat"] = 0
        self.lambda_mode["filter1"] = 4
        self.lambda_mode["filter2"] = 4
        self.lambda_mode["total_volume"] = 1
        self.lambda_mode["rest_time"] = 0
        self.lambda_mode["bot_microscope_data_shape"] = [1, 512, 512]
        self.lambda_mode["tracker_crop_size"] = 300
        self.lambda_mode["tracker_feature_size"] = 2500
        self.lambda_mode["tracker_camera_source"] = 1
        self.lambda_mode["stage_xy_limit"] = 10000
        self.lambda_mode["flir_camera_exposure_and_rate"] = [flir_exposure, int(1000000 / (1.02 * flir_exposure))]
        self.lambda_mode["stage_max_velocities"] = [1000, 1000]


        self.laser_405_vol_1 = tkinter.StringVar()
        self.laser_405_vol_2 = tkinter.StringVar()
        self.laser_405_vol_3 = tkinter.StringVar()
        self.laser_405_vol_4 = tkinter.StringVar()
        self.laser_488_vol_1 = tkinter.StringVar()
        self.laser_488_vol_2 = tkinter.StringVar()
        self.laser_488_vol_3 = tkinter.StringVar()
        self.laser_488_vol_4 = tkinter.StringVar()
        self.laser_561_vol_1 = tkinter.StringVar()
        self.laser_561_vol_2 = tkinter.StringVar()
        self.laser_561_vol_3 = tkinter.StringVar()
        self.laser_561_vol_4 = tkinter.StringVar()
        self.laser_640_vol_1 = tkinter.StringVar()
        self.laser_640_vol_2 = tkinter.StringVar()
        self.laser_640_vol_3 = tkinter.StringVar()
        self.laser_640_vol_4 = tkinter.StringVar()
        self.top_microscope_data_shape_z = tkinter.StringVar()
        self.top_microscope_data_shape_y = tkinter.StringVar()
        self.top_microscope_data_shape_x = tkinter.StringVar()
        self.bot_microscope_data_shape_z = tkinter.StringVar()
        self.bot_microscope_data_shape_y = tkinter.StringVar()
        self.bot_microscope_data_shape_x = tkinter.StringVar()
        self.tracker_camera_source = tkinter.StringVar()
        self.flir_camera_exposure = tkinter.StringVar()
        self.flir_camera_rate = tkinter.StringVar()
        self.tracker_feature_size = tkinter.StringVar()
        self.tracker_crop_size = tkinter.StringVar()
        self.z_resolution_in_um = tkinter.StringVar()
        self.zyla_camera_exposure_time_in_ms = tkinter.StringVar()
        self.filter1 = tkinter.StringVar()
        self.filter2 = tkinter.StringVar()
        self.total_volume = tkinter.StringVar()
        self.rest_time = tkinter.StringVar()
        self.stage_xy_limit = tkinter.StringVar()
        self.stage_max_velocity_xy = tkinter.StringVar()
        self.stage_max_velocity_z = tkinter.StringVar()
        self.zyla_camera_trigger_mode = tkinter.IntVar()
        self.dragonfly_imaging_mode = tkinter.IntVar()
        self.top_microscope_saving_mode = tkinter.IntVar()
        self.laser_output_repeat = tkinter.IntVar()
        self.bot_microscope_saving_mode = tkinter.IntVar()
        self.mode_name_to_load = tkinter.StringVar()
        self.reply = tkinter.StringVar()

        self.laser_405_vol_1.set("0.0")
        self.laser_405_vol_2.set("0.0")
        self.laser_405_vol_3.set("0.0")
        self.laser_405_vol_4.set("0.0")
        self.laser_488_vol_1.set("0.0")
        self.laser_488_vol_2.set("0.0")
        self.laser_488_vol_3.set("0.0")
        self.laser_488_vol_4.set("0.0")
        self.laser_561_vol_1.set("0.0")
        self.laser_561_vol_2.set("0.0")
        self.laser_561_vol_3.set("0.0")
        self.laser_561_vol_4.set("0.0")
        self.laser_640_vol_1.set("0.0")
        self.laser_640_vol_2.set("0.0")
        self.laser_640_vol_3.set("0.0")
        self.laser_640_vol_4.set("0.0")
        self.top_microscope_data_shape_z.set("25")
        self.top_microscope_data_shape_y.set("512")
        self.top_microscope_data_shape_x.set("512")
        self.bot_microscope_data_shape_z.set("1")
        self.bot_microscope_data_shape_y.set("512")
        self.bot_microscope_data_shape_x.set("512")
        self.tracker_camera_source.set("1")
        self.flir_camera_exposure.set("25000.0")
        self.flir_camera_rate.set("39.0")
        self.tracker_feature_size.set("2500")
        self.tracker_crop_size.set("300")
        self.z_resolution_in_um.set("1.0")
        self.zyla_camera_exposure_time_in_ms.set("10.0")
        self.filter1.set("4")
        self.filter2.set("4")
        self.total_volume.set("1")
        self.rest_time.set("0")
        self.stage_xy_limit.set("10000.0")
        self.stage_max_velocity_xy.set("1000.0")
        self.stage_max_velocity_z.set("1000.0")
        self.zyla_camera_trigger_mode.set(2)
        self.dragonfly_imaging_mode.set(1)
        self.top_microscope_saving_mode.set(0)
        self.laser_output_repeat.set(0)
        self.bot_microscope_saving_mode.set(0)
        self.reply.set("")

        self.laser_405_vol_1_entry = tkinter.Entry(
            self.window,
            textvariable=self.laser_405_vol_1,
            width=6
        )
        self.laser_405_vol_2_entry = tkinter.Entry(
            self.window,
            textvariable=self.laser_405_vol_2,
            width=6
        )
        self.laser_405_vol_3_entry = tkinter.Entry(
            self.window,
            textvariable=self.laser_405_vol_3,
            width=6
        )
        self.laser_405_vol_4_entry = tkinter.Entry(
            self.window,
            textvariable=self.laser_405_vol_4,
            width=6
        )
        self.laser_488_vol_1_entry = tkinter.Entry(
            self.window,
            textvariable=self.laser_488_vol_1,
            width=6
        )
        self.laser_488_vol_2_entry = tkinter.Entry(
            self.window,
            textvariable=self.laser_488_vol_2,
            width=6
        )
        self.laser_488_vol_3_entry = tkinter.Entry(
            self.window,
            textvariable=self.laser_488_vol_3,
            width=6
        )
        self.laser_488_vol_4_entry = tkinter.Entry(
            self.window,
            textvariable=self.laser_488_vol_4,
            width=6
        )
        self.laser_561_vol_1_entry = tkinter.Entry(
            self.window,
            textvariable=self.laser_561_vol_1,
            width=6
        )
        self.laser_561_vol_2_entry = tkinter.Entry(
            self.window,
            textvariable=self.laser_561_vol_2,
            width=6
        )
        self.laser_561_vol_3_entry = tkinter.Entry(
            self.window,
            textvariable=self.laser_561_vol_3,
            width=6
        )
        self.laser_561_vol_4_entry = tkinter.Entry(
            self.window,
            textvariable=self.laser_561_vol_4,
            width=6
        )
        self.laser_640_vol_1_entry = tkinter.Entry(
            self.window,
            textvariable=self.laser_640_vol_1,
            width=6
        )
        self.laser_640_vol_2_entry = tkinter.Entry(
            self.window,
            textvariable=self.laser_640_vol_2,
            width=6
        )
        self.laser_640_vol_3_entry = tkinter.Entry(
            self.window,
            textvariable=self.laser_640_vol_3,
            width=6
        )
        self.laser_640_vol_4_entry = tkinter.Entry(
            self.window,
            textvariable=self.laser_640_vol_4,
            width=6
        )
        self.top_microscope_data_shape_z_entry = tkinter.Entry(
            self.window,
            textvariable=self.top_microscope_data_shape_z,
            width=4
        )
        self.top_microscope_data_shape_y_entry = tkinter.Entry(
            self.window,
            textvariable=self.top_microscope_data_shape_y,
            width=4
        )
        self.top_microscope_data_shape_x_entry = tkinter.Entry(
            self.window,
            textvariable=self.top_microscope_data_shape_x,
            width=4
        )
        self.bot_microscope_data_shape_z_entry = tkinter.Entry(
            self.window,
            textvariable=self.bot_microscope_data_shape_z,
            width=4,
            state='disabled'
        )
        self.bot_microscope_data_shape_y_entry = tkinter.Entry(
            self.window,
            textvariable=self.bot_microscope_data_shape_y,
            width=4
        )
        self.bot_microscope_data_shape_x_entry = tkinter.Entry(
            self.window,
            textvariable=self.bot_microscope_data_shape_x,
            width=4
        )
        self.tracker_camera_source_entry = tkinter.Entry(
            self.window,
            textvariable=self.tracker_camera_source,
            width=8,
            state='disabled'
        )
        self.flir_camera_exposure_entry = tkinter.Entry(
            self.window,
            textvariable=self.flir_camera_exposure,
            width=8
        )
        self.flir_camera_rate_entry = tkinter.Entry(
            self.window,
            textvariable=self.flir_camera_rate,
            width=8
        )
        self.tracker_feature_size_entry = tkinter.Entry(
            self.window,
            textvariable=self.tracker_feature_size,
            width=8
        )
        self.tracker_crop_size_entry = tkinter.Entry(
            self.window,
            textvariable=self.tracker_crop_size,
            width=8
        )
        self.z_resolution_in_um_entry = tkinter.Entry(
            self.window,
            textvariable=self.z_resolution_in_um,
            width=7
        )
        self.zyla_camera_exposure_time_in_ms_entry = tkinter.Entry(
            self.window,
            textvariable=self.zyla_camera_exposure_time_in_ms,
            width=7
        )
        self.filter1_entry = tkinter.Entry(
            self.window,
            textvariable=self.filter1,
            width=7
        )
        self.filter2_entry = tkinter.Entry(
            self.window,
            textvariable=self.filter2,
            width=7
        )
        self.total_volume_entry = tkinter.Entry(
            self.window,
            textvariable=self.total_volume,
            width=7
        )
        self.rest_time_entry = tkinter.Entry(
            self.window,
            textvariable=self.rest_time,
            width=7
        )
        self.stage_xy_limit_entry = tkinter.Entry(
            self.window,
            textvariable=self.stage_xy_limit,
            width=7
        )
        self.stage_max_velocity_xy_entry = tkinter.Entry(
            self.window,
            textvariable=self.stage_max_velocity_xy,
            width=7
        )
        self.stage_max_velocity_z_entry = tkinter.Entry(
            self.window,
            textvariable=self.stage_max_velocity_z,
            width=7
        )
        self.current_mode_name = tkinter.Entry(
            self.window,
            width=15
        )
        self.command_entry = tkinter.Entry(
            self.window,
            width=200
        )
        self.reply_entry = tkinter.Entry(
            self.window,
            textvariable=self.reply,
            state='disabled',
            width=200,
        )
        self.load_button = tkinter.Menubutton(
            self.window, text="Load", relief='raised'
        )
        self.load_button.menu = tkinter.Menu(self.load_button, tearoff = 0)
        self.load_button["menu"] = self.load_button.menu
        self.set_mode_button = tkinter.Button(
            self.window, text="Set Displayed Parameters",
            command=self.set_current_mode_confirmation
        )
        self.zyla_camera_trigger_mode_radio_button_internal_trigger = tkinter.Radiobutton(
            self.window, text="Internal Trigger",
            variable=self.zyla_camera_trigger_mode, value=1,
            command=self.update_gui_mode
        )
        self.zyla_camera_trigger_mode_radio_button_external_trigger = tkinter.Radiobutton(
            self.window, text="External Trigger",
            variable=self.zyla_camera_trigger_mode, value=2,
            command=self.update_gui_mode
        )
        self.dragonfly_imaging_mode_radio_button_widefield = tkinter.Radiobutton(
            self.window, text="Wide-field",
            variable=self.dragonfly_imaging_mode, value=1,
            command=self.update_gui_mode
        )
        self.dragonfly_imaging_mode_radio_button_confocal_40um = tkinter.Radiobutton(
            self.window, text="Confocal 40um",
            variable=self.dragonfly_imaging_mode, value=2,
            command=self.update_gui_mode
        )
        self.dragonfly_imaging_mode_radio_button_confocal_25um = tkinter.Radiobutton(
            self.window, text="Confocal 25um",
            variable=self.dragonfly_imaging_mode, value=3,
            command=self.update_gui_mode
        )
        self.top_microscope_saving_mode_check_button = tkinter.Checkbutton(
            self.window, text="top microscope saving mode",
            offvalue=0, onvalue=1,
            variable=self.top_microscope_saving_mode,
            command=self.update_gui_mode
        )
        self.bot_microscope_saving_mode_check_button = tkinter.Checkbutton(
            self.window, text="bot microscope saving mode",
            offvalue=0, onvalue=1,
            variable=self.bot_microscope_saving_mode,
            command=self.update_gui_mode
        )
        self.laser_output_repeat_check_button = tkinter.Checkbutton(
            self.window, text="laser output repeat",
            offvalue=0, onvalue=1,
            variable=self.laser_output_repeat,
            command=self.update_gui_mode
        )
        self.laser_power_values = tkinter.Label(
            self.window,
            text="Laser Power Values",
            relief='ridge'
        )
        self.volume_1 = tkinter.Label(
            self.window,
            text = "Volume 1"
        )
        self.volume_2 = tkinter.Label(
            self.window,
            text = "Volume 2"
        )
        self.volume_3 = tkinter.Label(
            self.window,
            text = "Volume 3"
        )
        self.volume_4 = tkinter.Label(
            self.window,
            text = "Volume 4"
        )
        self.laser_405nm = tkinter.Label(
            self.window,
            text = "Laser 405nm"
        )
        self.laser_488nm = tkinter.Label(
            self.window,
            text = "Laser 488nm"
        )
        self.laser_561nm = tkinter.Label(
            self.window,
            text = "Laser 561nm"
        )
        self.laser_640nm = tkinter.Label(
            self.window,
            text = "Laser 640nm"
        )
        self.dataset_shape = tkinter.Label(
            self.window,
            text = "Dataset Shape",
            relief='ridge'
        )
        self.bottom = tkinter.Label(
            self.window,
            text = "Bottom"
        )
        self.top = tkinter.Label(
            self.window,
            text = "Top"
        )
        self.shape_z = tkinter.Label(
            self.window,
            text = "z"
        )
        self.shape_y = tkinter.Label(
            self.window,
            text = "y"
        )
        self.shape_x = tkinter.Label(
            self.window,
            text = "x"
        )
        self.bottom_microscope = tkinter.Label(
            self.window,
            text = "Bottom Microscope",
            relief='ridge'
        )
        self.tracker_source_cam_num = tkinter.Label(
            self.window,
            text = "Tracker Source (cam #)"
        )
        self.exposure_time = tkinter.Label(
            self.window,
            text = "Exposure Time (us)"
        )
        self.rate = tkinter.Label(
            self.window,
            text = "Rate (Hz)"
        )
        self.feature_size = tkinter.Label(
            self.window,
            text = "Feature Size (pixel)"
        )
        self.crop_size = tkinter.Label(
            self.window,
            text = "Crop Size (pixel)"
        )
        self.top_exposure_time = tkinter.Label(
            self.window,
            text = "Exposure Time (ms, divisible by 5)"
        )
        self.z_resolution = tkinter.Label(
            self.window,
            text = "Resolution in z (um)"
        )
        self.filter_channel_1 = tkinter.Label(
            self.window,
            text = "Channel 1 Filter"
        )
        self.filter_channel_2 = tkinter.Label(
            self.window,
            text = "Channel 2 Filter"
        )
        self.top_microscope = tkinter.Label(
            self.window,
            text = "Top Microscope",
            relief='ridge'
        )
        self.total_volumes = tkinter.Label(
            self.window,
            text = "Total Volumes"
        )
        self.resting_time = tkinter.Label(
            self.window,
            text = "Rest Time (s)"
        )
        self.stage_parameters = tkinter.Label(
            self.window,
            text = "Stage Parameters",
            relief='ridge'
        )
        self.travel_limit_xy = tkinter.Label(
            self.window,
            text = "Travel Limit (um)"
        )
        self.max_vel_xy = tkinter.Label(
            self.window,
            text = "X-Y Velocity Limit (um/s)"
        )
        self.max_vel_z = tkinter.Label(
            self.window,
            text = "Z Velocity Limit (um/s)"
        )
        self.zyla_trigger = tkinter.Label(
            self.window,
            text = "Zyla Camera Trigger Mode",
            relief='ridge'
        )
        self.dragonfly_pinhole = tkinter.Label(
            self.window,
            text = "Spinning Disk Pinhole",
            relief='ridge'
        )
        self.check_boxes = tkinter.Label(
            self.window,
            text = "Check Boxes",
            relief='ridge'
        )
        self.mode_save_load_set = tkinter.Label(
            self.window,
            text = "Save/Load/Set Imaging Modes",
            relief='ridge'
        )
        self.load_predefined_mode = tkinter.Label(
            self.window,
            text = "Load a Predefined Mode"
        )
        self.save_current_mode_as = tkinter.Label(
            self.window,
            text = "Save Current Mode As"
        )

        self.laser_405_vol_1_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.laser_405_vol_2_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.laser_405_vol_3_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.laser_405_vol_4_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.laser_488_vol_1_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.laser_488_vol_2_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.laser_488_vol_3_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.laser_488_vol_4_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.laser_561_vol_1_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.laser_561_vol_2_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.laser_561_vol_3_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.laser_561_vol_4_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.laser_640_vol_1_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.laser_640_vol_2_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.laser_640_vol_3_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.laser_640_vol_4_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.top_microscope_data_shape_z_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.top_microscope_data_shape_y_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.top_microscope_data_shape_x_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.bot_microscope_data_shape_z_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.bot_microscope_data_shape_y_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.bot_microscope_data_shape_x_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.tracker_camera_source_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.flir_camera_exposure_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.flir_camera_rate_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.tracker_feature_size_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.tracker_crop_size_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.z_resolution_in_um_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.zyla_camera_exposure_time_in_ms_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.filter1_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.filter2_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.total_volume_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.rest_time_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.stage_xy_limit_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.stage_max_velocity_xy_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.stage_max_velocity_z_entry.bind(
            '<Return>',
            lambda _: self.update_gui_mode()
        )
        self.current_mode_name.bind(
            '<Return>',
            lambda _: self.save()
        )
        self.load_button.bind(
            '<Button-1>',
            lambda _: self.prepare_load_button()
        )
        self.command_entry.bind(
            '<Return>',
            lambda _: self.send_command()
        )

        x1 = self.laser_405nm.winfo_reqwidth()
        x2 = self.volume_1.winfo_reqwidth()
        y1 = self.laser_power_values.winfo_reqheight()

        self.laser_power_values.place(
            x = self.x_spacing,
            y = self.y_spacing,
        )
        self.volume_1.place(
            x = 2 * self.x_spacing + x1,
            y = 2 * self.y_spacing + y1
        )
        self.volume_2.place(
            x = 3 * self.x_spacing + x1 + x2,
            y = 2 * self.y_spacing + y1
        )
        self.volume_3.place(
            x = 4 * self.x_spacing + x1 + 2 * x2,
            y = 2 * self.y_spacing + y1
        )
        self.volume_4.place(
            x = 5 * self.x_spacing + x1 + 3 * x2,
            y = 2 * self.y_spacing + y1
        )
        self.laser_405nm.place(
            x = self.x_spacing,
            y = 3 * self.y_spacing + 2 * y1
        )
        self.laser_488nm.place(
            x = self.x_spacing,
            y = 4 * self.y_spacing + 3 * y1
        )
        self.laser_561nm.place(
            x = self.x_spacing,
            y = 5 * self.y_spacing + 4 * y1
        )
        self.laser_640nm.place(
            x = self.x_spacing,
            y = 6 * self.y_spacing + 5 * y1
        )
        self.laser_405_vol_1_entry.place(
            x = 2 * self.x_spacing + x1,
            y = 3 * self.y_spacing + 2 * y1
        )
        self.laser_405_vol_2_entry.place(
            x = 3 * self.x_spacing + x1 + x2,
            y = 3 * self.y_spacing + 2 * y1
        )
        self.laser_405_vol_3_entry.place(
            x = 4 * self.x_spacing + x1 + 2 * x2,
            y = 3 * self.y_spacing + 2 * y1
        )
        self.laser_405_vol_4_entry.place(
            x = 5 * self.x_spacing + x1 + 3 * x2,
            y = 3 * self.y_spacing + 2 * y1
        )
        self.laser_488_vol_1_entry.place(
            x = 2 * self.x_spacing + x1,
            y = 4 * self.y_spacing + 3 * y1
        )
        self.laser_488_vol_2_entry.place(
            x = 3 * self.x_spacing + x1 + x2,
            y = 4 * self.y_spacing + 3 * y1
        )
        self.laser_488_vol_3_entry.place(
            x = 4 * self.x_spacing + x1 + 2 * x2,
            y = 4 * self.y_spacing + 3 * y1
        )
        self.laser_488_vol_4_entry.place(
            x = 5 * self.x_spacing + x1 + 3 * x2,
            y = 4 * self.y_spacing + 3 * y1
        )
        self.laser_561_vol_1_entry.place(
            x = 2 * self.x_spacing + x1,
            y = 5 * self.y_spacing + 4 * y1
        )
        self.laser_561_vol_2_entry.place(
            x = 3 * self.x_spacing + x1 + x2,
            y = 5 * self.y_spacing + 4 * y1
        )
        self.laser_561_vol_3_entry.place(
            x = 4 * self.x_spacing + x1 + 2 * x2,
            y = 5 * self.y_spacing + 4 * y1
        )
        self.laser_561_vol_4_entry.place(
            x = 5 * self.x_spacing + x1 + 3 * x2,
            y = 5 * self.y_spacing + 4 * y1
        )
        self.laser_640_vol_1_entry.place(
            x = 2 * self.x_spacing + x1,
            y = 6 * self.y_spacing + 5 * y1
        )
        self.laser_640_vol_2_entry.place(
            x = 3 * self.x_spacing + x1 + x2,
            y = 6 * self.y_spacing + 5 * y1
        )
        self.laser_640_vol_3_entry.place(
            x = 4 * self.x_spacing + x1 + 2 * x2,
            y = 6 * self.y_spacing + 5 * y1
        )
        self.laser_640_vol_4_entry.place(
            x = 5 * self.x_spacing + x1 + 3 * x2,
            y = 6 * self.y_spacing + 5 * y1
        )

        x3 = self.shape_x.winfo_reqwidth()
        x4 = self.top.winfo_reqwidth()
        x5 = self.bottom.winfo_reqwidth()
        x6 = 6 * self.x_spacing + x1 + 4 * x2 + 10 * self.x_spacing

        self.dataset_shape.place(
            x = x6,
            y = self.y_spacing
        )
        self.bottom.place(
            x = 2 * self.x_spacing + x6 + x3 + x4,
            y = 2 * self.y_spacing + y1
        )
        self.top.place(
            x = 1 * self.x_spacing + x6 + x3,
            y = 2 * self.y_spacing + y1
        )
        self.shape_z.place(
            x = x6,
            y = 3 * self.y_spacing + 2 * y1
        )
        self.shape_y.place(
            x = x6,
            y = 4 * self.y_spacing + 3 * y1
        )
        self.shape_x.place(
            x = x6,
            y = 5 * self.y_spacing + 4 * y1
        )
        self.top_microscope_data_shape_z_entry.place(
            x= 1 * self.x_spacing + x6 + x3,
            y= 3 * self.y_spacing + 2 * y1
        )
        self.top_microscope_data_shape_y_entry.place(
            x= 1 * self.x_spacing + x6 + x3,
            y= 4 * self.y_spacing + 3 * y1
        )
        self.top_microscope_data_shape_x_entry.place(
            x= 1 * self.x_spacing + x6 + x3,
            y= 5 * self.y_spacing + 4 * y1
        )
        self.bot_microscope_data_shape_z_entry.place(
            x= 2 * self.x_spacing + x6 + x3 + x4,
            y= 3 * self.y_spacing + 2 * y1
        )
        self.bot_microscope_data_shape_y_entry.place(
            x= 2 * self.x_spacing + x6 + x3 + x4,
            y= 4 * self.y_spacing + 3 * y1
        )
        self.bot_microscope_data_shape_x_entry.place(
            x= 2 * self.x_spacing + x6 + x3 + x4,
            y= 5 * self.y_spacing + 4 * y1
        )

        x7 = 3 * self.x_spacing + x6 + x3 + x4 + x5 + 10 * self.x_spacing
        x8 = max(self.tracker_source_cam_num.winfo_reqwidth(),
                 self.exposure_time.winfo_reqwidth(),
                 self.rate.winfo_reqwidth(),
                 self.feature_size.winfo_reqwidth(),
                 self.crop_size.winfo_reqwidth())
        x9 = self.tracker_camera_source_entry.winfo_reqwidth()

        self.bottom_microscope.place(
            x = x7,
            y = self.y_spacing
        )
        self.tracker_camera_source_entry.place(
            x = x7 + x8 + self.x_spacing,
            y = 2 * self.y_spacing + y1
        )
        self.flir_camera_exposure_entry.place(
            x = x7 + x8 + self.x_spacing,
            y = 3 * self.y_spacing + 2 * y1
        )
        self.flir_camera_rate_entry.place(
            x = x7 + x8 + self.x_spacing,
            y = 4 * self.y_spacing + 3 * y1
        )
        self.tracker_feature_size_entry.place(
            x = x7 + x8 + self.x_spacing,
            y = 5 * self.y_spacing + 4 * y1
        )
        self.tracker_crop_size_entry.place(
            x = x7 + x8 + self.x_spacing,
            y = 6 * self.y_spacing + 5 * y1,
        )
        self.tracker_source_cam_num.place(
            x = x7 ,
            y = 2 * self.y_spacing + y1
        )
        self.exposure_time.place(
            x = x7 ,
            y = 3 * self.y_spacing + 2 * y1
        )
        self.rate.place(
            x = x7 ,
            y = 4 * self.y_spacing + 3 * y1
        )
        self.feature_size.place(
            x = x7 ,
            y = 5 * self.y_spacing + 4 * y1
        )
        self.crop_size.place(
            x = x7 ,
            y = 6 * self.y_spacing + 5 * y1,
        )

        x10 = x7 + x8 + x9 + 2 * self.x_spacing + 10 * self.x_spacing
        x11 = max(self.z_resolution.winfo_reqwidth(),
                  self.top_exposure_time.winfo_reqwidth(),
                  self.filter_channel_1.winfo_reqwidth(),
                  self.filter_channel_2.winfo_reqwidth(),
                  self.total_volumes.winfo_reqwidth(),
                  self.resting_time.winfo_reqwidth())

        x12 = self.rest_time_entry.winfo_reqwidth()

        self.top_microscope.place(
            x = x10,
            y = self.y_spacing
        )
        self.z_resolution.place(
            x = x10,
            y = 2 * self.y_spacing + y1
        )
        self.top_exposure_time.place(
            x = x10,
            y = 3 * self.y_spacing + 2 * y1
        )
        self.filter_channel_1.place(
            x = x10,
            y = 4 * self.y_spacing + 3 * y1
        )
        self.filter_channel_2.place(
            x = x10,
            y = 5 * self.y_spacing + 4 * y1
        )
        self.total_volumes.place(
            x = x10,
            y = 6 * self.y_spacing + 5 * y1
        )
        self.resting_time.place(
            x = x10,
            y = 7 * self.y_spacing + 6 * y1
        )
        self.z_resolution_in_um_entry.place(
            x = x10 + x11 + self.x_spacing,
            y = 2 * self.y_spacing + y1
        )
        self.zyla_camera_exposure_time_in_ms_entry.place(
            x = x10 + x11 + self.x_spacing,
            y = 3 * self.y_spacing + 2 * y1
        )
        self.filter1_entry.place(
            x = x10 + x11 + self.x_spacing,
            y = 4 * self.y_spacing + 3 * y1
        )
        self.filter2_entry.place(
            x = x10 + x11 + self.x_spacing,
            y = 5 * self.y_spacing + 4 * y1
        )
        self.total_volume_entry.place(
            x = x10 + x11 + self.x_spacing,
            y = 6 * self.y_spacing + 5 * y1
        )
        self.rest_time_entry.place(
            x = x10 + x11 + self.x_spacing,
            y = 7 * self.y_spacing + 6 * y1
        )

        x13 = x10 + x11 + x12 + 2 * self.x_spacing + 10 * self.x_spacing
        x14 = max(self.travel_limit_xy.winfo_reqwidth(),
                  self.max_vel_xy.winfo_reqwidth(),
                  self.max_vel_z.winfo_reqwidth())
        x15 = self.stage_xy_limit_entry.winfo_reqwidth()


        self.stage_parameters.place(
            x = x13,
            y = self.y_spacing
        )
        self.travel_limit_xy.place(
            x = x13,
            y = 2 * self.y_spacing + y1
        )
        self.max_vel_xy.place(
            x = x13,
            y = 3 * self.y_spacing + 2 * y1
        )
        self.max_vel_z.place(
            x = x13,
            y = 4 * self.y_spacing + 3 * y1
        )
        self.stage_xy_limit_entry.place(
            x = x13 + x14 + self.x_spacing,
            y = 2 * self.y_spacing + y1
        )
        self.stage_max_velocity_xy_entry.place(
            x = x13 + x14 + self.x_spacing,
            y = 3 * self.y_spacing + 2 * y1
        )
        self.stage_max_velocity_z_entry.place(
            x = x13 + x14 + self.x_spacing,
            y = 4 * self.y_spacing + 3 * y1
        )

        x16 = x13 + x14 + x15 + 2 * self.x_spacing + 10 * self.x_spacing
        x17 = max(self.zyla_trigger.winfo_reqwidth(),
                  self.zyla_camera_trigger_mode_radio_button_internal_trigger.winfo_reqwidth(),
                  self.zyla_camera_trigger_mode_radio_button_external_trigger.winfo_reqwidth())

        self.zyla_trigger.place(
            x = x16,
            y = self.y_spacing
        )
        self.zyla_camera_trigger_mode_radio_button_internal_trigger.place(
            x = x16,
            y = 2 * self.y_spacing + y1
        )
        self.zyla_camera_trigger_mode_radio_button_external_trigger.place(
            x = x16,
            y = 3 * self.y_spacing + 2 * y1
        )

        x18 = x16 + x17 + self.x_spacing + 10 * self.x_spacing
        x19 = max(self.dragonfly_pinhole.winfo_reqwidth(),
                  self.dragonfly_imaging_mode_radio_button_widefield.winfo_reqwidth(),
                  self.dragonfly_imaging_mode_radio_button_confocal_25um.winfo_reqwidth(),
                  self.dragonfly_imaging_mode_radio_button_confocal_40um.winfo_reqwidth())
        self.dragonfly_pinhole.place(
            x = x18,
            y = self.y_spacing
        )
        self.dragonfly_imaging_mode_radio_button_widefield.place(
            x = x18,
            y = 2 * self.y_spacing + y1
        )
        self.dragonfly_imaging_mode_radio_button_confocal_40um.place(
            x = x18,
            y = 3 * self.y_spacing + 2 * y1
        )
        self.dragonfly_imaging_mode_radio_button_confocal_25um.place(
            x = x18,
            y = 4 * self.y_spacing + 3 * y1
        )

        x20 = x18 + x19 + self.x_spacing + 10 * self.x_spacing
        x21 = max(self.check_boxes.winfo_reqwidth(),
                  self.top_microscope_saving_mode_check_button.winfo_reqwidth(),
                  self.bot_microscope_saving_mode_check_button.winfo_reqwidth(),
                  self.laser_output_repeat_check_button.winfo_reqwidth())

        self.check_boxes.place(
            x = x20,
            y = self.y_spacing
        )
        self.top_microscope_saving_mode_check_button.place(
            x = x20,
            y = 2 * self.y_spacing + y1
        )
        self.bot_microscope_saving_mode_check_button.place(
            x = x20,
            y = 3 * self.y_spacing + 2 * y1
        )
        self.laser_output_repeat_check_button.place(
            x = x20,
            y = 4 * self.y_spacing + 3 * y1
        )


        x22 = x20 + x21 + self.x_spacing + 10 * self.x_spacing
        x23 = max(
            self.save_current_mode_as.winfo_reqwidth(),
            self.load_predefined_mode.winfo_reqwidth(),
        )
        x24 = self.current_mode_name.winfo_reqwidth()
        _ = max(
            self.load_button.winfo_reqwidth(),
            self.command_entry.winfo_reqwidth())

        self.mode_save_load_set.place(
            x = x22,
            y = self.y_spacing
        )
        self.load_predefined_mode.place(
            x = x22,
            y = 2 * self.y_spacing + y1
        )
        self.save_current_mode_as.place(
            x = x22,
            y = 3 * self.y_spacing + 2 * y1
        )
        self.current_mode_name.place(
            x = x22 + x23 + self.x_spacing,
            y = 3 * self.y_spacing + 2 * y1
        )
        self.load_button.place(
            x = x22 + x23 + self.x_spacing,
            y = y1 + 2 * self.y_spacing - 4
        )
        self.set_mode_button.place(
            x = x22,
            y = 3 * y1 + 4 * self.y_spacing
        )
        self.command_entry.place(
            x = self.x_spacing,
            y = 8 * self.y_spacing + 7 * y1
        )
        self.reply_entry.place(
            x = self.x_spacing,
            y = 9 * self.y_spacing + 8 * y1
        )


        self.update_gui_mode()
        self.window.protocol("WM_DELETE_WINDOW", self.shutdown)
        self.window.mainloop()

    def prepare_load_button(self):
        menu_len = self.load_button.menu.index(tkinter.END)
        if menu_len is not None:
            for _ in range(menu_len+1):
                self.load_button.menu.delete(0)

        with open(self.mode_filename, 'r') as f:
            modes_dict = json.load(f)
        mode_names = modes_dict.keys()

        for name in mode_names:
            self.load_button.menu.add_radiobutton(
                label=name,
                variable=self.mode_name_to_load,
                value=name,
                command=self.load)

    def set_current_mode_confirmation(self):
        is_permitted = tkinter.messagebox.askokcancel(
                'Imaging Mode',
                'Do you want to set displayed parameters?')
        if is_permitted:
            self.set_current_mode()

    def send_command(self):
        req_str = self.command_entry.get()
        if req_str=="":
            tkinter.messagebox.showerror('No Input', 'Command box is empty!')
        else:
            self.client.process(req_str)
            self.reply.set(self.client.reply)
            self._change_focus()

    def update_gui_mode(self):
        self._update_gui_mode()
        self._change_focus()
        self._compare_modes()

    def set_current_mode(self):
        self._update_gui_mode()
        self._set_current_mode()
        time.sleep(15)
        self._update_lambda_mode()
        self._compare_modes()

    def load(self):
        self._load()
        self._update_gui_mode()
        self._compare_modes()
        self.mode_name_to_load.set("")

    def save(self):
        self._update_gui_mode()
        self._save()
        self._compare_modes()

    def _save(self):
        mode_name = self.current_mode_name.get()
        with open(self.mode_filename, 'r') as f:
            modes_dict = json.load(f)
        mode_names = modes_dict.keys()

        if mode_name == '':
            tkinter.messagebox.showerror('Error', 'Mode name is missing!')

        elif mode_name in mode_names:
            is_permitted = tkinter.messagebox.askokcancel(
                'Overwrite Permission',
                'A mode with the same name exists, overwrite?')
            if is_permitted:
                modes_dict[mode_name] = self.gui_mode
                with open(self.mode_filename, 'w') as outfile:
                    json.dump(modes_dict, outfile, indent=4)
                tkinter.messagebox.showinfo(
                    'Successful Modification',
                    'Mode {} is successfully modified!'.format(mode_name))
        else:
            is_confirmed = tkinter.messagebox.askyesno(
                title="Saving Confirmation",
                message='Do you want to save current parameters as a new mode named {}?'.format(mode_name))
            if is_confirmed:
                modes_dict[mode_name] = self.gui_mode
                with open(self.mode_filename, 'w') as outfile:
                    json.dump(modes_dict, outfile, indent=4)
                tkinter.messagebox.showinfo('Successful Save', 'Mode {} is successfully saved!'.format(mode_name))

    def _load(self):
        mode_name = self.mode_name_to_load.get()
        with open(self.mode_filename, 'r') as f:
            modes_dict = json.load(f)
        mode = modes_dict[mode_name]

        self.top_microscope_saving_mode.set(mode["top_microscope_saving_mode"])
        self.zyla_camera_trigger_mode.set(mode["zyla_camera_trigger_mode"])
        self.dragonfly_imaging_mode.set(mode["dragonfly_imaging_mode"])
        self.top_microscope_data_shape_z.set(mode["top_microscope_data_shape"][0])
        self.top_microscope_data_shape_y.set(mode["top_microscope_data_shape"][1])
        self.top_microscope_data_shape_x.set(mode["top_microscope_data_shape"][2])
        self.z_resolution_in_um.set(mode["z_resolution_in_um"])
        self.zyla_camera_exposure_time_in_ms.set(mode["zyla_camera_exposure_time_in_ms"])
        self.laser_405_vol_1.set(mode["laser_power"][0][0])
        self.laser_405_vol_2.set(mode["laser_power"][0][1])
        self.laser_405_vol_3.set(mode["laser_power"][0][2])
        self.laser_405_vol_4.set(mode["laser_power"][0][3])
        self.laser_488_vol_1.set(mode["laser_power"][1][0])
        self.laser_488_vol_2.set(mode["laser_power"][1][1])
        self.laser_488_vol_3.set(mode["laser_power"][1][2])
        self.laser_488_vol_4.set(mode["laser_power"][1][3])
        self.laser_561_vol_1.set(mode["laser_power"][2][0])
        self.laser_561_vol_2.set(mode["laser_power"][2][1])
        self.laser_561_vol_3.set(mode["laser_power"][2][2])
        self.laser_561_vol_4.set(mode["laser_power"][2][3])
        self.laser_640_vol_1.set(mode["laser_power"][3][0])
        self.laser_640_vol_2.set(mode["laser_power"][3][1])
        self.laser_640_vol_3.set(mode["laser_power"][3][2])
        self.laser_640_vol_4.set(mode["laser_power"][3][3])
        self.laser_output_repeat.set(mode["laser_output_repeat"])
        self.filter1.set(mode["filter1"])
        self.filter2.set(mode["filter2"])
        self.total_volume.set(mode["total_volume"])
        self.rest_time.set(mode["rest_time"])
        self.bot_microscope_data_shape_z.set(mode["bot_microscope_data_shape"][0])
        self.bot_microscope_data_shape_y.set(mode["bot_microscope_data_shape"][1])
        self.bot_microscope_data_shape_x.set(mode["bot_microscope_data_shape"][2])
        self.bot_microscope_saving_mode.set(mode["bot_microscope_saving_mode"])
        self.tracker_crop_size.set(mode["tracker_crop_size"])
        self.tracker_feature_size.set(mode["tracker_feature_size"])
        self.tracker_camera_source.set(mode["tracker_camera_source"])
        self.stage_xy_limit.set(mode["stage_xy_limit"])
        self.flir_camera_exposure.set(mode["flir_camera_exposure_and_rate"][0])
        self.flir_camera_rate.set(mode["flir_camera_exposure_and_rate"][1])
        self.stage_max_velocity_xy.set(mode["stage_max_velocities"][0])
        self.stage_max_velocity_z.set(mode["stage_max_velocities"][1])

    def _set_current_mode(self):
        self.client.process("DO stop")

        for i in range(4):
            for j in range(4):
                self.client.process("DO _daq_set_laser {} {} {}".format(i, self.gui_mode["laser_power"][i][j], j))
        self.client.process("DO _daq_set_exposure_time {}".format(self.gui_mode["zyla_camera_exposure_time_in_ms"]))
        self.client.process("DO _daq_set_las_continuous {}".format(self.gui_mode["laser_output_repeat"]))
        self.client.process("DO _writer_set_saving_mode {}".format(self.gui_mode["top_microscope_saving_mode"]))
        self.client.process("DO _zyla_camera_set_trigger_mode {}".format(self.gui_mode["zyla_camera_trigger_mode"]))
        self.client.process("DO _dragonfly_set_imaging_mode {}".format(self.gui_mode["dragonfly_imaging_mode"]))
        self.client.process("DO _zyla_camera_set_shape {} {} {}".format(self.gui_mode["top_microscope_data_shape"][0],
                                                                         self.gui_mode["top_microscope_data_shape"][1],
                                                                         self.gui_mode["top_microscope_data_shape"][2]))
        self.client.process("DO _writer_set_shape {} {} {}".format(self.gui_mode["top_microscope_data_shape"][0],
                                                                    self.gui_mode["top_microscope_data_shape"][1],
                                                                    self.gui_mode["top_microscope_data_shape"][2]))
        self.client.process("DO _data_hub_set_shape {} {} {}".format(self.gui_mode["top_microscope_data_shape"][0],
                                                                      self.gui_mode["top_microscope_data_shape"][1],
                                                                      self.gui_mode["top_microscope_data_shape"][2]))
        self.client.process("DO _displayer_set_shape {} {} {}".format(self.gui_mode["top_microscope_data_shape"][0],
                                                                       self.gui_mode["top_microscope_data_shape"][1],
                                                                       self.gui_mode["top_microscope_data_shape"][2]))
        self.client.process("DO _daq_set_stack_size {}".format(self.gui_mode["top_microscope_data_shape"][0]))
        self.client.process("DO _daq_set_voltage_step {}".format(self.gui_mode["z_resolution_in_um"]))
        self.client.process("DO _dragonfly_set_filter 1 {}".format(self.gui_mode["filter1"]))
        self.client.process("DO _dragonfly_set_filter 2 {}".format(self.gui_mode["filter2"]))
        self.client.process("DO _data_hub_set_timer {} {}".format(self.gui_mode["total_volume"], self.gui_mode["rest_time"]))
        self.client.process("DO _stage_writer_set_saving_mode {}".format(self.gui_mode["bot_microscope_saving_mode"]))
        self.client.process("DO _tracker_set_feat_size {}".format(self.gui_mode["tracker_feature_size"]))
        self.client.process("DO _tracker_set_rate {}".format(self.gui_mode["flir_camera_exposure_and_rate"][1]))
        self.client.process("DO _zaber_set_limit_xy {}".format(self.gui_mode["stage_xy_limit"]))
        self.client.process("DO _zaber_set_max_velocities {} {}".format(self.gui_mode["stage_max_velocities"][0],
                                                                         self.gui_mode["stage_max_velocities"][1]))

        exp_diff = abs(float(self.gui_mode["flir_camera_exposure_and_rate"][0])-self.lambda_mode["flir_camera_exposure_and_rate"][0])
        exp_min = abs(min(float(self.gui_mode["flir_camera_exposure_and_rate"][0]) ,self.lambda_mode["flir_camera_exposure_and_rate"][0]))
        exp_ratio = exp_diff / exp_min
        fps_diff = abs(float(self.gui_mode["flir_camera_exposure_and_rate"][1])-self.lambda_mode["flir_camera_exposure_and_rate"][1])
        fps_min = abs(min(float(self.gui_mode["flir_camera_exposure_and_rate"][1]) ,self.lambda_mode["flir_camera_exposure_and_rate"][1]))
        fps_ratio = fps_diff / fps_min

        if self.gui_mode["bot_microscope_data_shape"][0] != self.lambda_mode["bot_microscope_data_shape"][0] or \
        self.gui_mode["bot_microscope_data_shape"][1] != self.lambda_mode["bot_microscope_data_shape"][1] or \
        self.gui_mode["bot_microscope_data_shape"][2] != self.lambda_mode["bot_microscope_data_shape"][2] or \
        self.gui_mode["tracker_camera_source"] != self.lambda_mode["tracker_camera_source"] or \
        exp_ratio > 0.04 or fps_ratio > 0.04:
            self.client.process("DO _flir_camera_stop")
            time.sleep(1)
            self.client.process("DO _tracker_set_camera_number {}".format(self.gui_mode["tracker_camera_source"]))
            self.client.process("DO _stage_data_hub_set_shape {} {} {}".format(self.gui_mode["bot_microscope_data_shape"][0],
                                                                               self.gui_mode["bot_microscope_data_shape"][1],
                                                                               self.gui_mode["bot_microscope_data_shape"][2]))
            self.client.process("DO _tracker_set_shape {} {} {}".format(self.gui_mode["bot_microscope_data_shape"][0],
                                                                        self.gui_mode["bot_microscope_data_shape"][1],
                                                                        self.gui_mode["bot_microscope_data_shape"][2]))
            self.client.process("DO _stage_writer_set_shape {} {} {}".format(self.gui_mode["bot_microscope_data_shape"][0],
                                                                             self.gui_mode["bot_microscope_data_shape"][1],
                                                                             self.gui_mode["bot_microscope_data_shape"][2]))
            self.client.process("DO _stage_displayer_set_shape {} {} {}".format(self.gui_mode["bot_microscope_data_shape"][0],
                                                                                self.gui_mode["bot_microscope_data_shape"][1],
                                                                                self.gui_mode["bot_microscope_data_shape"][2]))
            self.client.process("DO _flir_camera_set_height {}".format(self.gui_mode["bot_microscope_data_shape"][1]))
            self.client.process("DO _flir_camera_set_width {}".format(self.gui_mode["bot_microscope_data_shape"][2]))
            self.client.process("DO _flir_camera_set_exposure {} {}".format(self.gui_mode["flir_camera_exposure_and_rate"][0],
                                                                            self.gui_mode["flir_camera_exposure_and_rate"][1]))
            time.sleep(1)
            self.client.process("DO _flir_camera_start")
        self.client.process("DO _tracker_set_crop_size {}".format(self.gui_mode["tracker_crop_size"]))

    def _change_focus(self):
        current_widget = self.window.focus_get()
        current_widget_str = str(current_widget)
        if current_widget_str == ".!entry":
            current_widget_str = ".!entry1"

        if current_widget_str[:7] == ".!entry":
            entry_num = int(current_widget_str[7:])
            if 1 <= entry_num < 36:
                current_widget.tk_focusNext().focus()
                while self.window.focus_get().cget('state') == 'disabled':
                    self.window.focus_get().tk_focusNext().focus()

                pos = len(str(self.window.focus_get().get))
                self.window.focus_get().icursor(pos)
            else:
                self.window.focus_set()
        else:
            self.window.focus_set()

    def _update_gui_mode(self):
        self.gui_mode["top_microscope_saving_mode"] = self.top_microscope_saving_mode.get()
        self.gui_mode["zyla_camera_trigger_mode"] = self.zyla_camera_trigger_mode.get()
        self.gui_mode["dragonfly_imaging_mode"] = self.dragonfly_imaging_mode.get()
        self.gui_mode["top_microscope_data_shape"] = [int(self.top_microscope_data_shape_z.get()),
                                                      int(self.top_microscope_data_shape_y.get()),
                                                      int(self.top_microscope_data_shape_x.get())]
        self.gui_mode["z_resolution_in_um"] = float(self.z_resolution_in_um.get())
        self.gui_mode["zyla_camera_exposure_time_in_ms"] = float(self.zyla_camera_exposure_time_in_ms.get())
        self.gui_mode["laser_power"] = [[float(self.laser_405_vol_1.get()), float(self.laser_405_vol_2.get()),
                                         float(self.laser_405_vol_3.get()), float(self.laser_405_vol_4.get())],
                                        [float(self.laser_488_vol_1.get()), float(self.laser_488_vol_2.get()),
                                         float(self.laser_488_vol_3.get()), float(self.laser_488_vol_4.get())],
                                        [float(self.laser_561_vol_1.get()), float(self.laser_561_vol_2.get()),
                                         float(self.laser_561_vol_3.get()), float(self.laser_561_vol_4.get())],
                                        [float(self.laser_640_vol_1.get()), float(self.laser_640_vol_2.get()),
                                         float(self.laser_640_vol_3.get()), float(self.laser_640_vol_4.get())]]
        self.gui_mode["laser_output_repeat"] = self.laser_output_repeat.get()
        self.gui_mode["filter1"] = int(self.filter1.get())
        self.gui_mode["filter2"] = int(self.filter2.get())
        self.gui_mode["total_volume"] = int(self.total_volume.get())
        self.gui_mode["rest_time"] = int(self.rest_time.get())
        self.gui_mode["bot_microscope_data_shape"] = [int(self.bot_microscope_data_shape_z.get()),
                                                      int(self.bot_microscope_data_shape_y.get()),
                                                      int(self.bot_microscope_data_shape_x.get())]
        self.gui_mode["bot_microscope_saving_mode"] = self.bot_microscope_saving_mode.get()
        self.gui_mode["tracker_crop_size"] = int(self.tracker_crop_size.get())
        self.gui_mode["tracker_feature_size"] = int(self.tracker_feature_size.get())
        self.gui_mode["tracker_camera_source"] = int(self.tracker_camera_source.get())
        self.gui_mode["stage_xy_limit"] = float(self.stage_xy_limit.get())
        self.gui_mode["flir_camera_exposure_and_rate"] = [float(self.flir_camera_exposure.get()),
                                                          float(self.flir_camera_rate.get())]
        self.gui_mode["stage_max_velocities"] = [float(self.stage_max_velocity_xy.get()),
                                                 float(self.stage_max_velocity_z.get())]

    def _update_lambda_mode(self):
        try:
            self.client.process("GET writer{}".format(self.cam_num))
            rep = eval(self.client.reply)
            self.lambda_mode["top_microscope_saving_mode"] = int(rep["saving"])
        except Exception as e:
            print("Error from top writer: {}".format(e))
            self.lambda_mode["top_microscope_saving_mode"] = -1

        try:
            self.client.process("GET stage_writer1")
            rep = eval(self.client.reply)
            self.lambda_mode["bot_microscope_saving_mode"] = int(rep["saving"])
            self.lambda_mode["bot_microscope_data_shape"] = rep["shape"]
        except Exception as e:
            print("Error from bot writer: {}".format(e))
            self.lambda_mode["bot_microscope_saving_mode"] = -1
            self.lambda_mode["bot_microscope_data_shape"] = [1, -1, -1]

        try:
            self.client.process("GET ZylaCamera{}".format(self.cam_num))
            rep = eval(self.client.reply)
            if rep["trigger"] == "External":
                self.lambda_mode["zyla_camera_trigger_mode"] = 2
            elif rep["trigger"] == "Internal":
                self.lambda_mode["zyla_camera_trigger_mode"] = 1
            self.lambda_mode["top_microscope_data_shape"] = rep["shape"]
        except Exception as e:
            print("Error from zyla camera: {}".format(e))
            self.lambda_mode["zyla_camera_trigger_mode"] = -1
            self.lambda_mode["top_microscope_data_shape"] = [-1, -1, -1]

        try:
            self.client.process("GET dragonfly")
            rep = eval(self.client.reply)
            if rep["Pinhole Size"] == "NA":
                self.lambda_mode["dragonfly_imaging_mode"] = 1
            elif rep["Pinhole Size"] == "40um":
                self.lambda_mode["dragonfly_imaging_mode"] = 2
            elif rep["Pinhole Size"] == "25um":
                self.lambda_mode["dragonfly_imaging_mode"] = 3
            self.lambda_mode["filter1"] = int(rep["filter_1"])
            self.lambda_mode["filter2"] = int(rep["filter_2"])
        except Exception as e:
            print("Error from dragonfly: {}".format(e))
            self.lambda_mode["dragonfly_imaging_mode"] = -1
            self.lambda_mode["filter1"] = -1
            self.lambda_mode["filter2"] = -1

        try:
            self.client.process("GET daq")
            rep = eval(self.client.reply)
            self.lambda_mode["z_resolution_in_um"] = float(rep["voltage_step"]) * 10
            self.lambda_mode["zyla_camera_exposure_time_in_ms"] = float(rep["exposure_time"])
            self.lambda_mode["laser_power"][0] = get_array_from_str(rep["405nm"])
            self.lambda_mode["laser_power"][1] = get_array_from_str(rep["488nm"])
            self.lambda_mode["laser_power"][2] = get_array_from_str(rep["561nm"])
            self.lambda_mode["laser_power"][3] = get_array_from_str(rep["640nm"])
            self.lambda_mode["laser_output_repeat"] = int(rep["laser_output_repeat"])
        except Exception as e:
            print("Error from acquisition board: {}".format(e))
            self.lambda_mode["z_resolution_in_um"] = -1
            self.lambda_mode["zyla_camera_exposure_time_in_ms"] = -1
            self.lambda_mode["laser_power"][0] = [-1, -1, -1, -1]
            self.lambda_mode["laser_power"][1] = [-1, -1, -1, -1]
            self.lambda_mode["laser_power"][2] = [-1, -1, -1, -1]
            self.lambda_mode["laser_power"][3] = [-1, -1, -1, -1]
            self.lambda_mode["laser_output_repeat"] = -1

        try:
            self.client.process("GET data_hub{}".format(self.cam_num))
            rep = eval(self.client.reply)
            self.lambda_mode["total_volume"] = int(rep["total_volume"])
            self.lambda_mode["rest_time"] = int(rep["rest_time"])
        except Exception as e:
            print("Error from top data hub: {}".format(e))
            self.lambda_mode["total_volume"] = -1
            self.lambda_mode["rest_time"] = -1

        try:
            self.client.process("GET FlirCamera1")
            rep = eval(self.client.reply)
            self.lambda_mode["flir_camera_exposure_and_rate"][0] = float(rep["exposure"])
            self.lambda_mode["flir_camera_exposure_and_rate"][1] = float(rep["rate"])
        except Exception as e:
            print("Error from flir camera: {}".format(e))
            self.lambda_mode["flir_camera_exposure_and_rate"][0] = -1
            self.lambda_mode["flir_camera_exposure_and_rate"][1] = -1

        try:
            self.client.process("GET tracker")
            rep = eval(self.client.reply)
            self.lambda_mode["tracker_crop_size"] = int(rep["crop_size"])
            self.lambda_mode["tracker_feature_size"] = int(rep["feature_size"])
            self.lambda_mode["tracker_camera_source"] = int(rep["tracker_camera_source"])
        except Exception as e:
            print("Error from tracker: {}".format(e))
            self.lambda_mode["tracker_crop_size"] = -1
            self.lambda_mode["tracker_feature_size"] = -1
            self.lambda_mode["tracker_camera_source"] = -1

        try:
            self.client.process("GET zaber")
            rep = eval(self.client.reply)
            self.lambda_mode["stage_xy_limit"] = float(rep["stage_xy_limit"])
            self.lambda_mode["stage_max_velocities"][0] = float(rep["stage_max_xy_velocity"])
            self.lambda_mode["stage_max_velocities"][1] = float(rep["stage_max_z_velocity"])
        except Exception as e:
            print("Error from zaber: {}".format(e))
            self.lambda_mode["stage_xy_limit"] = -1
            self.lambda_mode["stage_max_velocities"][0] = -1
            self.lambda_mode["stage_max_velocities"][1] = -1

    def _compare_modes(self):
        self._decide_color(
            self.gui_mode["laser_output_repeat"],
            self.lambda_mode["laser_output_repeat"],
            self.laser_output_repeat_check_button
        )
        self._decide_color(
            self.gui_mode["filter1"],
            self.lambda_mode["filter1"],
            self.filter1_entry
        )
        self._decide_color(
            self.gui_mode["filter2"],
            self.lambda_mode["filter2"],
            self.filter2_entry
        )
        self._decide_color(
            self.gui_mode["total_volume"],
            self.lambda_mode["total_volume"],
            self.total_volume_entry
        )
        self._decide_color(
            self.gui_mode["rest_time"],
            self.lambda_mode["rest_time"],
            self.rest_time_entry
        )
        self._decide_color(
            self.gui_mode["bot_microscope_data_shape"][0],
            self.lambda_mode["bot_microscope_data_shape"][0],
            self.bot_microscope_data_shape_z_entry
        )
        self._decide_color(
            self.gui_mode["bot_microscope_data_shape"][1],
            self.lambda_mode["bot_microscope_data_shape"][1],
            self.bot_microscope_data_shape_y_entry
        )
        self._decide_color(
            self.gui_mode["bot_microscope_data_shape"][2],
            self.lambda_mode["bot_microscope_data_shape"][2],
            self.bot_microscope_data_shape_x_entry
        )
        self._decide_color(
            self.gui_mode["bot_microscope_saving_mode"],
            self.lambda_mode["bot_microscope_saving_mode"],
            self.bot_microscope_saving_mode_check_button
        )
        self._decide_color(
            self.gui_mode["tracker_crop_size"],
            self.lambda_mode["tracker_crop_size"],
            self.tracker_crop_size_entry
        )
        self._decide_color(
            self.gui_mode["tracker_feature_size"],
            self.lambda_mode["tracker_feature_size"],
            self.tracker_feature_size_entry
        )
        self._decide_color(
            self.gui_mode["tracker_camera_source"],
            self.lambda_mode["tracker_camera_source"],
            self.tracker_camera_source_entry
        )
        self._decide_color(
            self.gui_mode["stage_xy_limit"],
            self.lambda_mode["stage_xy_limit"],
            self.stage_xy_limit_entry
        )
        self._decide_color_uncertain(
            self.gui_mode["flir_camera_exposure_and_rate"][0],
            self.lambda_mode["flir_camera_exposure_and_rate"][0],
            self.flir_camera_exposure_entry
        )
        self._decide_color_uncertain(
            self.gui_mode["flir_camera_exposure_and_rate"][1],
            self.lambda_mode["flir_camera_exposure_and_rate"][1],
            self.flir_camera_rate_entry
        )
        self._decide_color(
            self.gui_mode["stage_max_velocities"][0],
            self.lambda_mode["stage_max_velocities"][0],
            self.stage_max_velocity_xy_entry
        )
        self._decide_color(
            self.gui_mode["stage_max_velocities"][1],
            self.lambda_mode["stage_max_velocities"][1],
            self.stage_max_velocity_z_entry
        )
        self._decide_color(
            self.gui_mode["top_microscope_saving_mode"],
            self.lambda_mode["top_microscope_saving_mode"],
            self.top_microscope_saving_mode_check_button
        )
        self._decide_color(
            self.gui_mode["zyla_camera_trigger_mode"],
            self.lambda_mode["zyla_camera_trigger_mode"],
            self.zyla_camera_trigger_mode_radio_button_external_trigger
        )
        self._decide_color(
            self.gui_mode["zyla_camera_trigger_mode"],
            self.lambda_mode["zyla_camera_trigger_mode"],
            self.zyla_camera_trigger_mode_radio_button_internal_trigger
        )
        self._decide_color(
            self.gui_mode["dragonfly_imaging_mode"],
            self.lambda_mode["dragonfly_imaging_mode"],
            self.dragonfly_imaging_mode_radio_button_confocal_25um
        )
        self._decide_color(
            self.gui_mode["dragonfly_imaging_mode"],
            self.lambda_mode["dragonfly_imaging_mode"],
            self.dragonfly_imaging_mode_radio_button_confocal_40um
        )
        self._decide_color(
            self.gui_mode["dragonfly_imaging_mode"],
            self.lambda_mode["dragonfly_imaging_mode"],
            self.dragonfly_imaging_mode_radio_button_widefield
        )
        self._decide_color(
            self.gui_mode["top_microscope_data_shape"][0],
            self.lambda_mode["top_microscope_data_shape"][0],
            self.top_microscope_data_shape_z_entry
        )
        self._decide_color(
            self.gui_mode["top_microscope_data_shape"][1],
            self.lambda_mode["top_microscope_data_shape"][1],
            self.top_microscope_data_shape_y_entry
        )
        self._decide_color(
            self.gui_mode["top_microscope_data_shape"][2],
            self.lambda_mode["top_microscope_data_shape"][2],
            self.top_microscope_data_shape_x_entry
        )
        self._decide_color(
            self.gui_mode["z_resolution_in_um"],
            self.lambda_mode["z_resolution_in_um"],
            self.z_resolution_in_um_entry
        )
        self._decide_color(
            self.gui_mode["zyla_camera_exposure_time_in_ms"],
            self.lambda_mode["zyla_camera_exposure_time_in_ms"],
            self.zyla_camera_exposure_time_in_ms_entry
        )
        self._decide_color(
            self.gui_mode["laser_power"][0][0],
            self.lambda_mode["laser_power"][0][0],
            self.laser_405_vol_1_entry
        )
        self._decide_color(
            self.gui_mode["laser_power"][0][1],
            self.lambda_mode["laser_power"][0][1],
            self.laser_405_vol_2_entry
        )
        self._decide_color(
            self.gui_mode["laser_power"][0][2],
            self.lambda_mode["laser_power"][0][2],
            self.laser_405_vol_3_entry
        )
        self._decide_color(
            self.gui_mode["laser_power"][0][3],
            self.lambda_mode["laser_power"][0][3],
            self.laser_405_vol_4_entry
        )
        self._decide_color(
            self.gui_mode["laser_power"][1][0],
            self.lambda_mode["laser_power"][1][0],
            self.laser_488_vol_1_entry
        )
        self._decide_color(
            self.gui_mode["laser_power"][1][1],
            self.lambda_mode["laser_power"][1][1],
            self.laser_488_vol_2_entry
        )
        self._decide_color(
            self.gui_mode["laser_power"][1][2],
            self.lambda_mode["laser_power"][1][2],
            self.laser_488_vol_3_entry
        )
        self._decide_color(
            self.gui_mode["laser_power"][1][3],
            self.lambda_mode["laser_power"][1][3],
            self.laser_488_vol_4_entry
        )
        self._decide_color(
            self.gui_mode["laser_power"][2][0],
            self.lambda_mode["laser_power"][2][0],
            self.laser_561_vol_1_entry
        )
        self._decide_color(
            self.gui_mode["laser_power"][2][1],
            self.lambda_mode["laser_power"][2][1],
            self.laser_561_vol_2_entry
        )
        self._decide_color(
            self.gui_mode["laser_power"][2][2],
            self.lambda_mode["laser_power"][2][2],
            self.laser_561_vol_3_entry
        )
        self._decide_color(
            self.gui_mode["laser_power"][2][3],
            self.lambda_mode["laser_power"][2][3],
            self.laser_561_vol_4_entry
        )
        self._decide_color(
            self.gui_mode["laser_power"][3][0],
            self.lambda_mode["laser_power"][3][0],
            self.laser_640_vol_1_entry
        )
        self._decide_color(
            self.gui_mode["laser_power"][3][1],
            self.lambda_mode["laser_power"][3][1],
            self.laser_640_vol_2_entry
        )
        self._decide_color(
            self.gui_mode["laser_power"][3][2],
            self.lambda_mode["laser_power"][3][2],
            self.laser_640_vol_3_entry
        )
        self._decide_color(
            self.gui_mode["laser_power"][3][3],
            self.lambda_mode["laser_power"][3][3],
            self.laser_640_vol_4_entry
        )

    def _decide_color(self, displayed_val, set_val, widget):
        if float(displayed_val) == float(set_val):
            widget.configure({"fg": "black"})
        else:
            widget.configure({"fg": "red"})

    def _decide_color_uncertain(self, displayed_val, set_val, widget):
        diff = abs(float(displayed_val)-set_val) / abs(min(float(displayed_val) ,set_val))
        if diff < 0.03:
            widget.configure({"fg": "black"})
        else:
            widget.configure({"fg": "red"})

    def shutdown(self):
        if tkinter.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.window.destroy()
            self.client.process("DO stop")
            self.client.process("DO shutdown")
            print(self.client.reply)


def get_array_from_str(string):
        list_ = string[1:-1].split(" ")
        out = []
        for element in list_:
            if element[-1]=='.':
                element = element[:-1]
            out.append(float(element))
        return out




def main():
    """CLI entry point."""

    args = docopt(__doc__)

    LambdaApp(client_port=int(args["--client_port"]),
              saving_mode=int(args["--saving_mode"]),
              zyla_camera_trigger_mode=int(args["--zyla_camera_trigger_mode"]),
              fmt=args["--format"],
              flir_exposure=float(args["--flir_exposure"]),
              zyla_camera=args["--zyla_camera"])


if __name__ == "__main__":
    main()
