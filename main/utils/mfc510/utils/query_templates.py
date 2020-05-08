def mfc5xx_chips(params):
    return {
        "image.raw": {"$exists": True},

    }


def mfc5xx_chips_w_source(params):
    return {
        "sourcefile": str(params["sourcefile"]).lower(),
        "image.raw": {"$exists": True},
        "$or": [
            {"image.y.chips" + params["version"] + "p" + str(params["y_level"]): {"$exists": False}},
            {"image.u.chips" + params["version"] + "p" + str(params["uv_level"]): {"$exists": False}},
            {"image.v.chips" + params["version"] + "p" + str(params["uv_level"]): {"$exists": False}}
        ]
    }


def mfc4xx_chips_depth(channel):
    """

    :param channel: should be left or right
    :return: str a mongoDB query
    """
    channel = str(channel)
    return {
        'image.'+channel+'.raw': {"$exists": True},
        "$or": [
            {'image.'+channel+'.y': {"$exists": False}},
            {'image.'+channel+'.u': {"$exists": False}},
            {'image.'+channel+'.v': {"$exists": False}}
        ]
    }


def q_img_exists(im_exists=True, sourcefile=None):
    if sourcefile:
        return {'image.raw': {"$exists": im_exists}, "sourcefile": str(sourcefile)}

    return {'image.raw': {"$exists": im_exists}}


def q_timestamp(ts, sourcefile=None):
    if sourcefile:
        return {"timestamp": int(ts), "sourcefile": str(sourcefile)}

    return {"timestamp": int(ts)}
