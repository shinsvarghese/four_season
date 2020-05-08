import multiprocessing
import ctypes
import os
import numpy as np

import cv2
from PIL import Image

from optparse import OptionParser
import pymongo
import gridfs as grid
from io import BytesIO
import hashlib
import time


def write_images_to_mongodb(imgs, gfs, collentry, coll, ptype, dll_version):
    if ptype not in ["chips","cipp1"]:
        ValueError("only 'chips' or 'cipp1' as type supported!")
    for img in imgs:
        enc_img = cv2.imencode(".png", img["data"])[1].tostring()
        hashid = get_hash_from_bytes(enc_img)
        fname = img["channel"] + "_" + str(collentry["sourcefile"]).replace('.rrec', '').replace('.rec', '') + "-" + str(collentry["timestamp"]) + ".png"
        gfs_res = gfs.find_one({"_id": hashid})
        if gfs_res is None:
            f_db = gfs.new_file(_id=hashid, filename=fname, contentType="image/png")
        # contentType = "image/png"
        # coll.insertImage(img,hashid,fname,contentType)
            try:
                res=f_db.write(enc_img)
                f_db.close()
                write_ok = True
                print('Write to gridfs successful!')
            except:
                write_ok = False
                print(collentry["_id"])
                print("Write to gridfs failed!")
                # continue
        else:
            print('File already exists, updating image link...')
            write_ok = True

        # gfs_res = gfs.find_one({"_id": hashid})
        # if gfs_res is None:
        #     write_ok = False
        # else:
        #     write_ok = True

        if write_ok:
            pyramid_tag = ''
            if img["channel"] == 'yp3':
                pyramid_tag = 'p3'
                scale_x = 0.5
                scale_y = 0.5
            if img["channel"] == 'y':
                pyramid_tag = 'p2'
                scale_x = 1.0
                scale_y = 1.0
            elif img["channel"] == 'u':
                pyramid_tag = 'p3'
                scale_x = 0.5
                scale_y = 0.5
            elif img["channel"] == 'v':
                pyramid_tag = 'p3'
                scale_x = 0.5
                scale_y = 0.5
            else:
                ValueError('channel should be y,u or v')

            if ptype == "cipp1":
                shift_x = 80
                shift_y = 0
                pyramid_tag = ''
                dll_version = ''
            elif ptype == "chips":
                shift_x = 0
                shift_y = 0
            else:
                ValueError('proc_type not supported!')

            # if img["channel"] == 'y':
            #     scale_x = 1.0
            #     scale_y = 1.0
            # else:
            #     scale_x = 0.5
            #     scale_y = 0.5

            doc = {"tool_version":"1.1","slope": img["slope"],
                   "scale_x": scale_x,"scale_y": scale_y,"shift_x": shift_x,
                   "shift_y": shift_y, "hash": hashid, "size_x": img["data"].shape[1],
                   "size_y": img["data"].shape[0], ptype + "_version": dll_version,
                   "isp_configuration": "SWI_MFC510_CP_2018_11_22_05_27_14"}
            if 'image' in collentry.keys():
                if img["channel"][0] in collentry["image"].keys():
                    # channel present, write only ptype
                    collentry["image"][img["channel"][0]][ptype+dll_version + pyramid_tag] = doc
                else:
                    #no channel present, write including channel
                    collentry["image"][img["channel"][0]] = {ptype + dll_version + pyramid_tag: doc}
                    # collentry["image"][img["channel"]] = {ptype : doc}
            else:
                # no image present, write complete image entry
                # collentry["image"] = {img["channel"]: {ptype: doc}}
                collentry["image"] = {img["channel"][0] + dll_version + pyramid_tag: {ptype: doc}}
            coll.update_one({"_id": collentry["_id"]}, {"$set": {"image":collentry["image"]}})
            print("inserted in ...", collentry["_id"])
def call_dll(imgData=None, requestSlope=int(0), ptype="chips"):
    error = 0
    if ptype == "chips":
        if requestSlope not in [0,1]:
            ValueError("RequestSlope must be in [0 = Day, 1 = Night]")
    elif ptype == "cipp1":
        if requestSlope not in [4]:
            ValueError("RequestSlope must be in [4 = Day, ? = Night]")
    else:
        ValueError("proc type not supported, use 'cipp1' or 'chips'")

    image = imgData["data"].tobytes()
    width = imgData["width"]
    height = imgData["height"]

    # init output arrays
    imageOutY = ctypes.create_string_buffer(1500 * 1500 * 2)
    widthOutY = ctypes.c_int(0)
    heightOutY = ctypes.c_int(0)

    imageOutU = ctypes.create_string_buffer(1500 * 1500 * 1)
    widthOutU = ctypes.c_int(0)
    heightOutU = ctypes.c_int(0)

    imageOutV = ctypes.create_string_buffer(1500 * 1500 * 1)
    widthOutV = ctypes.c_int(0)
    heightOutV = ctypes.c_int(0)

    if ptype == "chips":
        try:
            orgPath=os.getcwd()
            os.chdir(orgPath+"\\dlls")
            chips_dll = ctypes.CDLL("Chips2.dll")
            os.chdir(orgPath)
        except:
            error=1
            ValueError("cannot open chips.dll")
            raise
        # start = time.clock()
        # chips_dll = ctypes.CDLL("Chips.dll")
        try:
            chips_dll.runChips(ctypes.c_char_p(image), ctypes.c_int(width), ctypes.c_int(height), ctypes.c_int(int(requestSlope)),
                              ctypes.pointer(imageOutY), ctypes.byref(widthOutY), ctypes.byref(heightOutY),
                              ctypes.pointer(imageOutU), ctypes.byref(widthOutU), ctypes.byref(heightOutU),
                              ctypes.pointer(imageOutV), ctypes.byref(widthOutV), ctypes.byref(heightOutV))
        except:
            print("Warning ! could not run chips dll")
            error=1
        #stop = time.clock()
        #elapsedTime = stop - start
    elif ptype == "cipp1":
        try:
            cipp_dll = ctypes.CDLL("cippDll_64.dll")
        except:
            cipp_dll = None
            ValueError("cannot open cipp.dll")
        cfaRedGreen = float(1.23)
        cfaGreenRef = float(1)
        cfaBlueGreen = float(0.43)
        #requestSlope = int(4)
        blackLevel = int(167)

        #start = time.clock()
        cipp_dll.runCipp(ctypes.c_char_p(image), ctypes.c_int(width), ctypes.c_int(height), ctypes.c_int(int("0x00008000", 0)),
                         ctypes.c_float(cfaRedGreen), ctypes.c_float(cfaGreenRef), ctypes.c_float(cfaBlueGreen),
                         ctypes.c_int(requestSlope), ctypes.c_int(blackLevel),
                         ctypes.pointer(imageOutY), ctypes.byref(widthOutY), ctypes.byref(heightOutY),
                         ctypes.pointer(imageOutU), ctypes.byref(widthOutU), ctypes.byref(heightOutU),
                         ctypes.pointer(imageOutV), ctypes.byref(widthOutV), ctypes.byref(heightOutV))
        #stop = time.clock()
        #elapsedTime = stop - start

    else:
        ValueError('only type "chips" or "chipp" supported!')



    out = list()
    outY = np.frombuffer(imageOutY, np.uint16)
    outY = outY[:heightOutY.value * widthOutY.value].reshape((heightOutY.value, widthOutY.value))
    if ptype == "chips":
        sh=np.shape(outY)
        outYP3= zoom_to_size(outY,[int(sh[0]/2),int(sh[1]/2)])
        out.append({"data": outYP3, "channel": "yp3", "slope": requestSlope})
    out.append({"data":outY, "channel":"y", "slope" : requestSlope})

    outU = np.frombuffer(imageOutU, np.uint8)
    outU = outU[:heightOutU.value * widthOutU.value].reshape((heightOutU.value, widthOutU.value))
    out.append({"data": outU, "channel": "u", "slope" : requestSlope})

    outV = np.frombuffer(imageOutV, np.uint8)
    outV = outV[:heightOutV.value * widthOutV.value].reshape((heightOutV.value, widthOutV.value))
    out.append({"data": outV, "channel": "v", "slope" : requestSlope})

    return out,error

def zoom_to_size(x, size, interpolation=cv2.INTER_LINEAR):
    """
    zoom the tensor x to the given size by linear interpolation or another interpolation method
    :param x: input tensor, remains constant
    :param size: scale factor for each channel in tensor
    :param interpolation: interpolation method
    :return: the zoomed tensor
    """
    assert (isinstance(size, tuple) or isinstance(size, list) or isinstance(size, np.ndarray))
    ipm = interpolation  # interpolation method
    if len(size) != len(x.shape):
        assert (len("shape length has to match") == 0)
    if len(size) == 2:  # singe channel image
        # open cv needs columns first in resize function
        ret = cv2.resize(x, (size[1], size[0]), interpolation=ipm)
    else:
        ret = None
        assert (len("tensor size is not supported") == 0)
    assert (list(ret.shape) == list(size))
    return ret

def get_hash_from_bytes(data):

    return hashlib.md5(data).hexdigest()


def process(params):

    client = pymongo.MongoClient(params["params"]["uri"])
    db = client[params["params"]["db"]]
    coll = db[params["params"]["coll"]]
    #
    gfs = grid.GridFS(db, "image_data")

    # gfs=   coll.getGridFs()
    ptype = params["params"]["proc_type"]
    collentry=coll.find_one({"_id":params["doc"]["_id"]})

    # collentry =  params["doc"]
    if "image" in collentry.keys():
        # try:
        #     if collentry['image']['raw']['size_y'] != 640:
        #         return
        # except :
        #     pass
        hash = collentry["image"]["raw"]["hash"]
        width = collentry["image"]["raw"]["size_x"]
        height = collentry["image"]["raw"]["size_y"]
        gridOut = gfs.find_one({"_id": hash})
        if gridOut is not None:
            # read raw image and convert to numpy
            imgData = gridOut.read()
            imgData = Image.open(BytesIO(imgData))

            imgData = np.asarray(imgData).astype(np.uint16)
            if ptype == "chips":
                new_width = 1152
                new_height = 640
            else:
                new_width = width
                new_height = height

            imgData = imgData[0:new_height, 0:new_width]
            try:
                image_output,error = call_dll(imgData={"data":imgData,"height":new_height, "width": new_width}, requestSlope=params["params"]["slope"], ptype=ptype)
                if 0:
                    #cv2.imshow("RAW_Img", imgData*16)
                    for out in image_output:
                        # show y image
                        if out["channel"]=="y":
                            cv2.imshow(ptype + "_Y", out["data"] * 16)
                    cv2.waitKey(0)
                else:
                    if error == 0:
                        write_images_to_mongodb(image_output, gfs, collentry,coll, ptype, "2")

            except Exception as e:
                print(e)
                pass
        else:
            print("no image found in gridfs!")
def mainProcess(coll,signlist,countryList,uri,d,col,limit=0,skip=0,thread=None,lightCondition=None):
    startTime = time.time()

    proc_type= 'chips'
    slope ='0'

    client = pymongo.MongoClient(uri)
    # cl = pymongo.MongoClient(options.uri)
    db = client[d]

    gridfs = grid.GridFS(db, "image_data")
    coll = db[col]
    query={"image.raw.hash": {"$exists": 1},"image.y.chips2p2": {"$exists": False}, 'image.raw.size_y':640,'sourcefolder':{'$nin':[
    "N/A",
    "N/A two or more hits!"
]}}
    if lightCondition is not None:
        if lightCondition=="Night":
            query["annotations.framelabel.light_conditions.value"]={"$ne":"Day"}
        else:
            query["annotations.framelabel.light_conditions.value"]="Day"
    if signlist:
        query['annotations.boxlabel.attributes.sign_class.value']={'$in':signlist}
    if countryList:
        query['annotations.framelabel.country.value']={'$in':countryList}

    for cname in range(1):  # for cname in range(1,164):
        # c = db[("%03d") % cname]
        if thread != None:
            print("Chips conversion initiated in thread ....... {0}".format(str(thread)))
        else:
            print("Chips conversion initiated ")

        # ids = list(coll.find(query,{"_id": 1}).limit(5))
        docs = list(coll.find(query,{"_id":1}).sort('timestamp',1).skip(skip).limit(limit))
        print("......")
        if len(docs) >0:
            print(len(docs))
            params = dict()
            params["uri"] = uri
            params["db"] = d
            params["coll"] = col
            params["slope"] = slope

            params["proc_type"] = proc_type
            collection=coll
            # # params["coll"]=coll
            try:
                pool = multiprocessing.Pool(processes=2)
                results = pool.map(process, [{"doc": doc, "params": params} for doc in docs])
            except:
                return

        # endTime=time.time()-startTime
        # print(endTime)
        # results=process({"ids":ids[0],"params":params})
        #
        #
        # for doc in docs:
        #     process({"doc": doc, "params": params})
        if thread != None:
            print("Conversion Completed in thread....{0}".format(str(thread)))
        else:
            print("Chipes Conversion Completed ")
        return
if __name__ == "__main__":
    multiprocessing.freeze_support()
    startTime=time.time()

    parser = OptionParser()
    parser.add_option("--uri", dest="uri", help="source mongodb URI like mongodb://user:pass@hostname")
    parser.add_option("--d", dest="db_name", help="source mongodb database name")
    parser.add_option("--c", dest="collection_name", help="source mongodb collection name")
    parser.add_option("--proc_type", dest="proc_type", help="processing type could either be 'cipp1' or 'chips'")
    parser.add_option("--slope", dest="slope", help="slope, day=0, night=1",type = "int")

    (options, args) = parser.parse_args()

    client = pymongo.MongoClient(options.uri)
    # cl = pymongo.MongoClient(options.uri)
    db = client[options.db_name]


    gridfs = grid.GridFS(db, "image_data")
    coll = db[options.collection_name]

    # try:
    #chips_dll = ctypes.CDLL("Chips2.dll")
    # except:
    #     chips_dll = None
    #     logging.error("cannot open Chips.dll")

    #cursor = coll.find({"sourcefile":"20140423_0509_{e73023f4-6c14-49f6-8605-31f8612e3320}.rrec", "timestamp": 1398231162147601})
    for cname in range(1):  #for cname in range(1,164):
        # c = db[("%03d") % cname]

        docs = coll.find({"image.raw": {"$exists": 1},'image.raw.size_y':640,"annotations.framelabel.light_conditions.value": "Day"} )
        #pymongo.errors.ServerSelectionTimeoutError: ozd2257u.conti.de:27017: timed out
        params = dict()
        params["uri"] = options.uri
        params["db"] = options.db_name
        params["coll"]=options.collection_name
        params["slope"] = options.slope


        params["proc_type"] = options.proc_type


        # pool = multiprocessing.Pool(processes=2)
        # results = pool.map(process, [{"ids": id, "params": params} for id in ids])
        # endTime=time.time()-startTime
        # print(endTime)
        # results=process({"ids":ids[0],"params":params})

        try:
            pool = multiprocessing.Pool(processes=2)
            results = pool.map(process, [{"doc": doc, "params": params} for doc in docs])
        except:
            pass

        # for doc in docs:
        #    process({"doc": doc, "params": params})






