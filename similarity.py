import math
import numpy as np
import cv2
from similarity import utils

FLANN_INDEX_KDTREE = 0

'''Further reading on moment calculations and the algorithms used below:
    
    https://en.wikipedia.org/wiki/Image_moment
    https://en.wikipedia.org/wiki/Central_moment
    https://en.wikipedia.org/wiki/Moment_(mathematics)
    https://en.wikipedia.org/wiki/Standardized_moment
'''
def make_moment(arr) -> dict:
    arr = np.array(arr)

    assert len(arr.shape) == 2

    # define the moment dictionary
    moment = {}

    # make a mesh grid for calculating the moments weight
    # with the same size as arr
    x_size, y_size = np.mgrid[:arr.shape[0], :arr.shape[1]]

    # calculate the mean of x and y
    moment["x_mean"] = np.sum(x_size * arr) / np.sum(arr)
    moment["y_mean"] = np.sum(y_size*arr) / np.sum(arr)

    # calculate spacial moments of the moment
    moment["m00"] = np.sum(arr)
    moment["m01"] = np.sum(x_size * arr)
    moment["m10"] = np.sum(y_size * arr)
    moment["m11"] = np.sum(x_size*y_size*arr)
    moment["m02"] = np.sum((x_size**2)*arr)
    moment["m20"] = np.sum((y_size**2)*arr)
    moment["m12"] = np.sum(y_size*(x_size**2)*arr)
    moment["m21"] = np.sum(x_size*(y_size**2)*arr)
    moment["m03"] = np.sum((x_size**3)*arr)
    moment["m30"] = np.sum((y_size**3)*arr)

    # central moments
    moment["mu01"] = 0
    moment["mu10"] = 0
    moment["mu11"] = np.sum((x_size-moment["x_mean"])*(y_size-moment["y_mean"])*arr)
    moment["mu02"] = np.sum((y_size - moment["y_mean"])**2 * arr)
    moment["mu20"] = np.sum((x_size - moment["x_mean"])**2 * arr)
    moment["mu12"] = np.sum((x_size - moment["x_mean"]) * ((y_size - moment["y_mean"])**2) * arr)
    moment["mu21"] = np.sum(((x_size - moment["x_mean"])**2) * (y_size - moment["y_mean"]) * arr)
    moment["mu03"] = np.sum(((y_size - moment["y_mean"])**3) * arr)
    moment["mu30"] = np.sum(((x_size - moment["x_mean"])**3) * arr)

    # central scale invariant moments
    moment["nu11"] = moment["mu11"] / (np.sum(arr)**float(2/2+1))
    moment["nu12"] = moment["mu12"] / (np.sum(arr)**float(5/2))
    moment["nu21"] = moment["mu21"] / (np.sum(arr)**float(5/2))
    moment["nu20"] = moment["mu20"] / (np.sum(arr)**float(2/2+1))
    moment["nu02"] = moment["mu02"] / (np.sum(arr)**float(2/2+1))
    moment["nu30"] = moment["mu30"] / (np.sum(arr)**float(5/2))
    moment["nu03"] = moment["mu03"] / (np.sum(arr)**float(5/2))

    return moment


def make_moment_from_contour(contour):
    return cv2.moments(contour)

'''The algorithm for calculating hu moments can be understood here:
    https://www.learnopencv.com/shape-matching-using-hu-moments-c-python/
'''
def calculate_hu_moment(moment: dict) -> list:
    hu_values = [0]*7
    t0 = moment["nu30"] + moment["nu12"]
    t1 = moment["nu21"] + moment["nu03"]

    q0 = t0 * t0
    q1 = t1 * t1

    n4 = 4 * moment["nu11"]
    s = moment["nu20"] + moment["nu02"]
    d = moment["nu20"] - moment["nu02"]

    hu_values[0] = s
    hu_values[1] = d * d + n4 * moment["nu11"]
    hu_values[3] = q0 + q1
    hu_values[5] = d * (q0 - q1) + n4 * t0 * t1

    t0 *= q0 - 3 * q1
    t1 *= 3 * q0 - q1

    q0 = moment["nu30"] - 3 * moment["nu12"]
    q1 = 3 * moment["nu21"] - moment["nu03"]

    hu_values[2] = q0 * q0 + q1 * q1
    hu_values[4] = q0 * t0 + q1 * t1
    hu_values[6] = q1 * t0 - q0 * t1

    return hu_values


def log_normalize(hu_values: list) -> list:
    ret = [0.0]*6
    for i in range(0, 6):
        abs_i = math.fabs(hu_values[i])
        multiplier = 1 if hu_values[i] > 0 else -1 if hu_values[i] < 0 else 0
        ret[i] = multiplier * math.log10(abs_i)

    return ret

def calculate_score(hu_moments1, hu_moments2):
    # calculate the euclidean distance from each hu moment to determine similarity
    # NOTE: we can drop the 7th vector from both as it simply denotes if the two objects are reflected
    score = 0
    for x in range(0, 6):
        # score += abs(hu_moments1[x] - hu_moments2[x])
        score += (hu_moments1[x] - hu_moments2[x])**2

    score = math.sqrt(score)
    return score

def shape_similarity(image1, image2):
    # get the hu moments
    hu_moments1 = calculate_hu_moment(make_moment(image1))
    hu_moments2 = calculate_hu_moment(make_moment(image2))

    # log transform the hu moments for more normalized numbers
    hu_moments1 = log_normalize(hu_moments1)
    hu_moments2 = log_normalize(hu_moments2)

    return calculate_score(hu_moments1, hu_moments2)


def contour_similarity(template, comparison):
    hu_moment_template = log_normalize(calculate_hu_moment(cv2.moments(template)))
    hu_moment_comparison = log_normalize(calculate_hu_moment(cv2.moments(comparison)))

    score = 0
    for x in range(6):
        # if hu_moment_template[x] > eps and hu_moment_comparison[x] > eps:
        score += math.fabs(hu_moment_comparison[x] - hu_moment_template[x])

    return score