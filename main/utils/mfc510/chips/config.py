# from pypwd import PasswordManager

mongo_test_host = 'ozd0127u:27018'
mongo_prod_host = 'ozd0127u:27018'
mongo_gridfs_default = 'image_data'

prod_base_uri = "mongodb://{}:{}@" + mongo_prod_host
test_base_uri = "mongodb://{}:{}@" + mongo_test_host

# mongodb_user = "writeMfc520_test_labels"
# pm = PasswordManager()


mfc510_sample_noannot = {
    "uri": prod_base_uri,#.format(mongodb_user, pm.get_user_password(mongodb_user)),
    'db': 'Labels',
    'coll': 'Shape_Latest_7_Classes_BackUp',
    'gridfs': 'image_data',
   # "img_dir": "//lud2a9cw/dataset/mfc510_demo_rec_sampling/selected_frames_bin/2019.07.05_at_08.07.46_camera-mi_146.rrec/",
    "frequency": 1,
    "version": "2",
    "y_level": 2,
    "uv_level": 3,
    "slope": 0,
    #"sourcefile": "2019.01.16_at_17.12.34_camera-mi_101.rrec",
    "is_licensed": 0,
    "processes": 0
}
mfc4xx_sample_noannot_={
    "uri": prod_base_uri,  # .format(mongodb_user, pm.get_user_password(mongodb_user)),
    'db': 'Labels',
    'coll': 'Shape_Latest_7_Classes_BackUp',
    'gridfs': 'image_data',
    # "img_dir": "//lud2a9cw/dataset/mfc510_demo_rec_sampling/selected_frames_bin/2019.07.05_at_08.07.46_camera-mi_146.rrec/",
    "frequency": 1,
    "version": "2",
    "y_level": 2,
    "uv_level": 3,
    "slope": 0,
    # "sourcefile": "2019.01.16_at_17.12.34_camera-mi_101.rrec",
    "is_licensed": 0,
    "processes": 0
}
mongo_write_recording_noannot = "write_recording_noannot"
#
# mfc4xx_sample_noann = {
#     "uri": prod_base_uri.format(mongo_write_recording_noannot, pm.get_user_password(mongo_write_recording_noannot)),
#     'db': 'recording_noannot',
#     'coll': 'mfc4xx_noannot',
#     'gridfs': 'mfc4xx_noannot',
#     "img_dir": "//lud2a9cw/dataset/samasource_publicate/mfc520/selected/OD_Set1_20190226_city_600/2019.01.16_at_17.12.34_camera-mi_101/",
#     "version": "2",
#     "y_level": 2,
#     "uv_level": 3,
#     "proc_type": "chips",
#     "sourcefile": "snapshot_2015.06.08_at_16.24.18.rec",
#     "slope": 0,
#     "is_licensed": 0,
#     "processes": 0
# }
#
# mfc4xx_depth_latest = {
#     "uri": prod_base_uri.format(mongo_write_recording_noannot, pm.get_user_password(mongo_write_recording_noannot)),
#     'db': 'depth_labels',
#     'coll': 'latest_test',
#     'gridfs': 'latest_test',
#     'base_dir': 'D:/workspace/depth/07_04/right/',
#     "img_dir": "//lifs010s.cw01.contiwan.com/workbench/Output/20150925_1521_{832c1eba-6a97-4416-8cec-46fc6b146ba0}_mfc4xx/MFC4xx_long_image_left_png/",
#     "version": "",
#     "y_level": 2,
#     "uv_level": 3,
#     "frequency": 8,
#     "channel": "left",
#     "proc_type": "chips",
#     "slope": 0,
#     "is_licensed": 0,
#     "processes": 0
# }
#
# mfc510_sample_noannot_ = {
#     "uri": prod_base_uri.format(mongodb_user, pm.get_user_password(mongodb_user)),
#     'db': 'recording_noannot',
#     'coll': 'mfc510_noannot',
#     'gridfs': 'mfc510_noannot',
#     "img_dir": "//lud2a9cw/dataset/mfc510_demo_rec_sampling/selected_frames_bin/2019.07.05_at_08.07.46_camera-mi_146.rrec/",
#     "frequency": 1,
#     "version": "2",
#     "y_level": 2,
#     "uv_level": 3,
#     "slope": 0,
#     "sourcefile": "2019.01.16_at_17.12.34_camera-mi_101.rrec",
#     "is_licensed": 0,
#     "processes": 0
# }
