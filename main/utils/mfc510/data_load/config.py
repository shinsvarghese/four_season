from pypwd import PasswordManager

mongo_test_host = 'luas114x.lu.de.conti.de'
mongo_prod_host = 'luas100x.lu.de.conti.de'
mongo_gridfs_default = 'image_data'

prod_base_uri = "mongodb://{}:{}@" + mongo_prod_host
test_base_uri = "mongodb://{}:{}@" + mongo_test_host

mongodb_user = "writeMfc520_test_labels"
pm = PasswordManager()


mfc510_sample_noannot = {
    "uri": prod_base_uri.format(mongodb_user, pm.get_user_password(mongodb_user)),
    'db': 'recording_noannot',
    'coll': 'mfc510_noannot',
    'gridfs': 'mfc510_noannot',
    "img_dir": "//lud2a9cw/dataset/mfc510_demo_rec_sampling/selected_frames_bin/2019.07.05_at_08.07.46_camera-mi_146.rrec/",
    "frequency": 1,
    "version": "2",
    "y_level": 2,
    "uv_level": 3,
    "slope": 1,
    "sourcefile": "2019.01.16_at_17.12.34_camera-mi_101.rrec",
    "processes": 0
}
