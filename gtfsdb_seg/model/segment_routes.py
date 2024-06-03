from sqlalchemy import Column, String, Numeric
from gtfsdb import Stop, Trip, Shape, PatternBase

from .base import Base
from ott.utils import geo_utils

import logging
log = logging.getLogger(__file__)


class SegmentRoutes(Base, PatternBase):
    __tablename__ = 'seg_routes'

    def __init__(self, session, route):
        super(SegmentRoutes, self).__init__()
        self.id = route

    """
    ## define relationships
    stop_segment = relationship(
        'SegmentStops',
        primaryjoin='SegmentTrips.segment_id==SegmentStops.id',
        foreign_keys='(SegmentTrips.segment_id)',
        uselist=False, viewonly=True
    )
    """

    @classmethod
    def load(cls, session, do_trip_segments=True, chunk_size=10000, do_print=True):
        """
        will find all stop-stop pairs from stop_times/trip data, and create stop-stop segments in the database
        """
        # import pdb; pdb.set_trace()

    @classmethod
    def to_geojson(cls, session):
        """
        override the default to_geojson
        {
          "type": "FeatureCollection",
          "features": [
            {"type":"Feature", "properties":{"id":"1-2"}, "geometry":{"type":"LineString","coordinates":[[-122.677388,45.522879],[-122.677396,45.522913]]}},
            {"type":"Feature", "properties":{"id":"2-3"}, "geometry":{"type":"LineString","coordinates":[[-122.675715,45.522215],[-122.67573,45.522184]]}},
          ]
        }
        """

