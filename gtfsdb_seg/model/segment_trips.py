from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base

import logging
log = logging.getLogger(__file__)


class SegmentTrips(Base):
    __tablename__ = 'seg_trips'

    segment_id = Column(String(255), index=True, nullable=False)
    trip_id = Column(String(255), index=True, nullable=False)
    shape_id = Column(String(255), nullable=False)
    service_id = Column(String(255), nullable=False)
    route_id = Column(String(255), nullable=False)
    route_id = Column(String(255), nullable=False)
    route_sort_order = Column(Integer)
    mode = Column(String(255))

    ## define relationships
    stop_segment = relationship(
        'SegmentStops',
        primaryjoin='SegmentTrips.segment_id==SegmentStops.id',
        foreign_keys='(SegmentTrips.segment_id)',
        uselist=False, viewonly=True
    )

    '''
    sqlalchemy.exc.NoReferencedTableError: Foreign key associated with column 'seg_trips.trip_id' could not find table 'trips' with which to generate a foreign key to target column 'trip_id'
    sqlalchemy.exc.ArgumentError: Could not locate any relevant foreign key columns for primary join condition 'trimet.trips.trip_id = :trip_id_1' on relationship SegmentTrips.trip.  Ensure that referencing columns are associated with a ForeignKey or ForeignKeyConstraint, or are annotated in the join condition with the foreign() annotation.

    from gtfsdb import Trip
    #trip_id = Column(String(255), ForeignKey("trips.trip_id"), primary_key=True, nullable=False)
    trip = relationship(
        Trip,
        primaryjoin=Trip.trip_id=="SegmentTrips.trip_id",
        foreign_keys='(SegmentTrips.trip_id)',
        uselist=False, viewonly=True)
    '''

    def __init__(self, session, segment, trip):
        super(SegmentTrips, self).__init__()
        self.id = "{}-{}".format(segment.id, trip.trip_id)
        self.segment_id = segment.id
        self.trip_id = trip.trip_id
        self.shape_id = trip.shape_id
        self.service_id = trip.service_id
        self.route_id = trip.route.route_id
        self.route_sort_order = trip.route.route_sort_order
        self.mode = trip.route.type.otp_type
