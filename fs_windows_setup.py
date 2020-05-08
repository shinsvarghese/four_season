# --------------------------------------------
# setup script for the redvine toolchain (to be called from rv_start.bat)
# Martin Pfitzer
# 2017-07-04
# --------------------------------------------

from __future__ import print_function

import configparser
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile


def is_proxy_running():
    import psutil  # import in this function scope since psutil might not be installed yet (-> exception is caught)
    return "cntlm.exe" in (p.name() for p in psutil.process_iter())


def read_configfile():
    print('parsing configfile...')
    cfg = configparser.ConfigParser()
    cfg.read(r'fs_windows.ini')
    return cfg


def write_configfile(cfg):
    with open(r'fs_windows.ini', 'w') as fp:
        cfg.write(fp)


def setup_venv():
    ''' setting up the virtual environment (will be started from the parent batch script) '''
    cfg = read_configfile()

    print('creating virtual python environment...')
    py_path = cfg['PATHS']['Python']
    if '"' in py_path:
        py_path = py_path.split('"')[1]
    os.system('"' + os.path.join(py_path, 'python') + '" -m venv .\env ')


def get_win_compatible_path(path):
    '''
    When calling a program from a path it needs to be checked if the path contains spaces -> then it needs to be encapsulated in " ", if no space is in the path the " " need to be removed
    '''
    if ' ' in path and '"' not in path:
        path = '"' + path + '"'  # put path with spaces in " "
    if ' ' not in path and '"' in path:
        path = path.split('"')[1]  # if "" are there, but no spaces are in the path, windows will complain
    return path

def get_env_compatible_path(path):
    '''
    when adding paths to the windows %PATH% variable, leading and trailing " " need to be removed!
    '''
    return path.replace('"', '')

def setup_start():
    ''' update python modules, set environment and prepare a console/ide '''
    cfg = read_configfile()
    # cfg_actions = [el[0] for el in cfg['ACTIONS'].items()]
    # if 'startlocalmongodb' not in cfg_actions:
        # print('WARNING: startlocalmongodb option not provided in rv_windows.ini, assuming default [FALSE]')
        # cfg['ACTIONS']['startlocalmongodb'] = 'False'
    # if 'installgitlfs' not in cfg_actions:
        # print('WARNING: installgitlfs option not provided in rv_windows.ini, assuming default [TRUE]')
        # cfg['ACTIONS']['installgitlfs'] = 'True'
    # if 'startgui' not in cfg_actions:
        # print('WARNING: startgui option not provided in rv_windows.ini, assuming default [FALSE]')
        # cfg['ACTIONS']['startgui'] = 'False'
    # if 'installcianti' not in cfg_actions:
        # print('WARNING: installcianti option not provided in rv_windows.ini, assuming default [TRUE]')
        # cfg['ACTIONS']['installcianti'] = 'True'

    os.environ['pythonDir'] = cfg['PATHS']['Python']

    # configure the venv
    download_files = dict()  # store tuple of (target_location, source_location).
    # store zip files including version - in order to skip the download if files already exist
    download_files['tools'] = ('tools/tools_v1.1.1.zip',
                               'http://github.conti.de/ADAS-Machine-Learning/redvine/releases/download/v1.1.1/tools.zip')
    download_files['libs'] = ('env/install/libs_v1.3.0.zip',
                              'http://github.conti.de/ADAS-Machine-Learning/redvine/releases/download/v1.2.1/libs_v1.3.0.zip')
    # #download_files['gitlfs'] = ('tools/gitlfs_v2.3.4.zip',
                                # #'http://github.conti.de/ADAS-Machine-Learning/redvine/releases/download/v1.1.1/git-lfs-windows-amd64-2.3.4.zip')
    download_files['python_embed'] = ('tools/python-3.5.2-embed-amd64.zip',
                                      'http://github.conti.de/ADAS-Machine-Learning/redvine/releases/download/v1.1.1/python-3.5.2-embed-amd64.zip')
    # download_files['cianti'] = ('env/install/cianti-1.1.0-cp35-none-win_amd64.whl',
                              # 'http://github.conti.de/ADAS-Machine-Learning/redvine/releases/download/v1.3.0/cianti-1.1.0-cp35-none-win_amd64.whl')
    # download_files['shapely'] = ('env/install/Shapely-1.6.4.post1-cp35-cp35m-win_amd64.whl',
                                # 'http://github.conti.de/ADAS-Machine-Learning/redvine/releases/download/v1.3.0/Shapely-1.6.4.post1-cp35-cp35m-win_amd64.whl')
                                      
    # if cfg['ACTIONS']['StartLocalMongoDb'] == 'True':
        # download_files['mongodb'] = ('env/install/mongodb_win_v3.4.0.zip',
                                     # 'http://github.conti.de/ADAS-Machine-Learning/redvine/releases/download/v1.1.1/mongodb_win_v3.4.0.zip')

    # print('Beginning large binary file download...')

    for loc in download_files.values():
        if not os.path.isdir(os.path.dirname(loc[0])):
            os.makedirs(os.path.dirname(loc[0]))

        if not os.path.isfile(loc[0]):
            urllib.request.urlretrieve(loc[1], loc[0])
    print('Download successful!')

    # start with the Git LFS installation (since this is failing most often in order to get the according error message at a well visible place)
    # if cfg['ACTIONS']['installgitlfs']:
        # gitpath = cfg['PATHS']['git']
        # if os.path.isfile(os.path.join(gitpath, 'git-lfs.exe')):
            # subprocess.run([os.path.join(gitpath, 'git-lfs.exe'), "install"])
        # elif os.path.isfile(os.path.join(gitpath, '..', 'bin', 'git-lfs.exe')):
            # subprocess.run([os.path.join(gitpath, '..', 'bin', 'git-lfs.exe'), "install"])            
        # elif os.path.isfile(os.path.join(gitpath, '..', 'cmd', 'git-lfs.exe')):
            # subprocess.run([os.path.join(gitpath, '..', 'cmd', 'git-lfs.exe'), "install"])
        # else:
            # if not os.path.isfile('./tools/gitlfs/git-lfs.exe'):
                # os.mkdir('./tools/gitlfs')
                # with zipfile.ZipFile(download_files['gitlfs'][0], 'r') as zipf:
                    # zipf.extractall('tools\gitlfs')
            # try:
                # shutil.copyfile(r'.\tools\gitlfs\git-lfs.exe', os.path.join(gitpath, 'git-lfs.exe'))
                # subprocess.run([os.path.join(gitpath, 'git-lfs.exe'), "install"])
            # except:
                # raise ValueError('Your Git installation does not seem to include git-lfs. Please update your git installation to a current version or manually copy the git-lfs.exe into your git/bin directory. You can find the git-lfs.exe in the ./tool directory')
    #
    if not os.path.isfile(r'env/EnvironmentSuccessfullyConfigured.txt'):
        with zipfile.ZipFile(download_files['libs'][0], 'r') as zipf:
            zipf.extractall('env/install')
        with zipfile.ZipFile(download_files['tools'][0], 'r') as zipf:
            zipf.extractall('tools')
        with zipfile.ZipFile(download_files['python_embed'][0], 'r') as zipf:
            zipf.extract(member='python3.dll', path='.\env\Scripts')

        os.system(r'xcopy /I /Y /S "%pythonDir%\Lib\site-packages\scipy\*.*" .\env\Lib\site-packages\scipy')
        os.system(r'xcopy /I /Y /S "%pythonDir%\Lib\site-packages\scipy-0.18.1-py3.5-win-amd64.egg-info\*.*" .\env\Lib\site-packages\scipy-0.18.1-py3.5-win-amd64.egg-info')
        os.system(r'xcopy /I /Y /S "%pythonDir%\Library\*.*" .\env\Library')
        os.system(r'xcopy /I /Y /S .\tools\graphviz-2.38\*.* .\env\Library\bin')
        os.system(r'xcopy /I /Y /S .\env\install\ecal\*.* .\env\lib\site-packages')
        with open(r'env/EnvironmentSuccessfullyConfigured.txt', 'a') as file:
            pass

    # setup connection_params.ini file if it doesn't already exist
    # if not os.path.isfile(os.path.join(r"D:\RedVine\redvine-Develop", 'db', 'connection_params.ini')):
    #     shutil.copyfile(os.path.join(r"D:\RedVine\redvine-Develop", 'db', 'connection_params.ini.template'),
    #                     os.path.join(r"D:\RedVine\redvine-Develop", 'db', 'connection_params.ini'))

    # some python installations might set the system variable PIP_CONFIG_FILE leading to the pip command not working
    if 'PIP_CONFIG_FILE' in os.environ:
        os.environ['PIP_CONFIG_FILE'] = get_win_compatible_path(
            os.path.join(os.getcwd(), 'env', 'pip.conf'))  # overwrite with proper settings

    if cfg['ACTIONS']['StartProxy'] == 'True':
        try:
            proxy_running = is_proxy_running()
        except:
            proxy_running = False

        if not proxy_running:
            os.system('start tools\proxyCntlm\RunProxyInteractively.bat')
            input("Please enter your password in the proxy command window and press enter here...")

    if cfg['ACTIONS']['UpdatePip'] == 'True':
        os.system('env\Scripts\python.exe -m pip install --upgrade pip --proxy localhost:8879')
        os.system(r'env\Scripts\python.exe -m pip install -r requirements.txt --proxy localhost:8879')

        # special handling for modules which are not available via pip:
        #os.system(r'env\Scripts\python.exe -m pip install env\install\Shapely-1.6.4.post1-cp35-cp35m-win_amd64.whl')  # manually install this via a wheel package since it includes some .dll dependencies which are not available via pip install under windows !

    os.environ['PYTHONPATH'] = os.getcwd()
    
    # if cfg['ACTIONS']['InstallCianti'] == 'True':
        #os.system(r'D:\RedVine\redvine-Develop\env\Scripts\python.exe -m pip install env/install/cianti-1.1.0-cp35-none-win_amd64.whl --proxy localhost:8879')

    # install jupyter kernelspec
    #os.system(r'D:\RedVine\redvine-Develop\env\Scripts\python.exe -m ipykernel install --user --name=redvine')

    # adding cuda, git to path
#    for addpath in [cfg['PATHS']['CudnnLib'], cfg['PATHS']['CudaToolkit'], cfg['PATHS']['Git']]:
      #  addpath = get_env_compatible_path(addpath)
        # add to sys path
       # os.environ['PATH'] = addpath + os.pathsep + os.environ['PATH']

    # set Keras backend
    os.environ['KERAS_BACKEND'] = 'tensorflow'
    back_end = 'Set Backend as Tensorflow'
    # for i in range(2, len(sys.argv)):
            # if sys.argv[i] == '-c':
                # #CNTK specific installation
                # print('Setting up CNTK backend')
                # os.system('python -m pip install cntk-gpu==2.5.1 --proxy localhost:8879')
                # os.environ['KERAS_BACKEND'] = 'cntk'
                # back_end ='Set Backend as CNTK'
            # else:
                # print('Unknown option')
    # print(back_end)

    os.environ['PYTHONPATH'] += os.pathsep + os.path.join(os.getcwd(), 'data',
                                                          'protobuf')  # to resolve dependencies between compiled protobuf files, the path needs to be added to the sys.path :/

    # if cfg['ACTIONS']['StartLocalMongoDb'] == 'True':
        # mongodb_path = './env/mongodb'
        # if not os.path.isdir(mongodb_path):
            # # initial installation of mongodb
            # os.makedirs(mongodb_path)
            # os.makedirs(os.path.join(mongodb_path, 'data'))
            # os.makedirs(os.path.join(mongodb_path, 'log'))
            # with zipfile.ZipFile(download_files['mongodb'][0], 'r') as zipf:
                # zipf.extractall(mongodb_path)

        # # start the mongodb server
        # os.chdir(mongodb_path)
        # start_command = 'start "MongoDB Server" {} --config "{}"'.format(os.path.join('bin', 'mongod.exe'),
                                                                         # 'mongod_win.conf')
        # os.system(start_command)
        # os.chdir('../..')

    if cfg['ACTIONS']['StartIDE'] == 'True':
        command = 'start "" ' + get_win_compatible_path(cfg['PATHS']['IDE'])
        if 'pycharm' in cfg['PATHS']['IDE'].lower():
            command += ' ' + os.getcwd()  # start pycharm in current folder
            print('Launching Pycharm IDE via: ' + command)
        os.system(command)

    if cfg['ACTIONS']['StartGUI'] == 'True':
        os.system('start gui\start_server.bat')
        print('GUI is starting...')

    # open console with all environment variables set
    try:
        cmd_path = os.path.join(os.environ['WINDIR'], "System32")
        if cmd_path not in os.environ['PATH']:
            # add location of cmd.exe
            os.environ['PATH'] += os.pathsep + cmd_path
    except:
        pass

    if len(sys.argv) > 2 and sys.argv[2] != '-c':
        # it is possible to specify some args to rv_start.bat which would be executed directly (1-click starter for net)
        # e.g. call rv_start.bat "cd main && python LostAndFound_Roman.py"
        with open(r'env\tmp_starter.bat', 'w') as f:
            f.write(sys.argv[2])

        os.system(r'env\tmp_starter.bat')
    else:
        # open console with all environment variables set
        os.system('cmd')


if __name__ == '__main__':
    try:
        if sys.argv[1] == 'venv':
            setup_venv()
        elif sys.argv[1] == 'start':
            setup_start()
        else:
            raise UserWarning
    except UserWarning:
        print('invalid argument use "venv" or "start"')
