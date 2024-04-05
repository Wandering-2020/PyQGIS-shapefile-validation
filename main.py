import datetime
import logging
import os

from modules import fields
from modules import intersections
from modules import lengths
from utilities import configure_logger

FILE_PATH = os.path.expanduser("~/Downloads/1/PW Scenarios - 1.shp")
LAYER = QgsVectorLayer(FILE_PATH, "", "ogr")
# iface.addVectorLayer(FILE_PATH, '', 'ogr')

INDEX = QgsSpatialIndex()

MIN_BOUND = 20
MAX_BOUND = 1000

DISTANCE_AREA = QgsDistanceArea()
DISTANCE_AREA.setEllipsoid("WGS84")
CRS = QgsCoordinateReferenceSystem("EPSG:4326")
DISTANCE_AREA.setSourceCrs(CRS, QgsProject.instance().transformContext())

configure_logger.configure_logger(
    os.path.dirname(os.path.realpath(__file__)),
    datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
)


def main():
    logger = logging.getLogger("QGIS_logger")

    feedback_message = ""
    null_geoms = set()

    fieldCheck = fields.Fields(LAYER)
    fieldCheck.run()

    intersectionCheck = intersections.Intersections(
        layer=LAYER,
        index=INDEX,
    )
    intersection_nulls = intersectionCheck.run()
    null_geoms.update(intersection_nulls)

    lengthCheck = lengths.Lengths(
        layer=LAYER,
        min_bound=MIN_BOUND,
        max_bound=MAX_BOUND,
        distance_area=DISTANCE_AREA,
    )
    length_nulls = lengthCheck.run()
    null_geoms.update(length_nulls)

    result, message = fieldCheck.getFeedback()
    if result:
        feedback_message += message

    result, message = intersectionCheck.getFeedback()
    if result:
        feedback_message += message

    result, message = lengthCheck.getFeedback()
    if result:
        feedback_message += message

    if null_geoms:
        logger.error(f"{len(null_geoms)} features have Null geometry")
        logger.info(f"features with Null geometry: {null_geoms}")

    return feedback_message


feedback_message = main()
if feedback_message:
    print(feedback_message)
