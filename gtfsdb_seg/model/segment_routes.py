from sqlalchemy import Column, String, Numeric
from sqlalchemy.sql.functions import func

from gtfsdb import Stop, Trip, Shape, PatternBase


from .base import Base
from ott.utils import geo_utils

import logging
log = logging.getLogger(__file__)


def XgetOffsetAmounts(factor, dir, offset=0.000035):
    ret_val = 0, 0
    if factor > 0:
        x = y = 0
        if   dir == "N":  x =  1;  y =  0;
        elif dir == "NE": x =  1;  y =  1;
        elif dir == "NW": x =  1;  y = -1;
        elif dir == "S":  x = -1;  y =  0;
        elif dir == "SE": x = -1;  y = -1;
        elif dir == "SW": x = -1;  y =  1;
        elif dir == "E":  x =  0;  y =  1;
        elif dir == "W":  x =  0;  y = -1;
        else: print("hmm", dir)  ## import pdb; pdb.set_trace() 
        ret_val = x * offset * factor, y * offset * factor
    return ret_val


def XoffsetGeom(session, geom, x, y):
    ret_val = geom
    if x or y:
        ret_val = session.scalar(func.ST_Translate(geom, x,  y))
        #ret_val = geom.ST_Simplify()
    return ret_val


def offsetGeom(session, geom, x, y):
    ret_val = geom
    if x or y:
        ret_val = session.scalar(func.ST_OffsetCurve(geom, x))
        #ret_val = geom.ST_Simplify()
    return ret_val

def getOffsetAmounts(factor, dir, offset=0.000035):
    ret_val = 0, 0
    if factor > 0:
        if dir in ("N", "E", "SE" "NE"): x =  1;  y =  1;
        else: x = 1; y = 1; # dir in ("N", "E", "SE" "NE"): x =  1;  y =  1;
        ret_val = x * offset * factor, y * offset * factor
    return ret_val


def etl(trips):
    routes_segs = {}

    for t in trips:
        r = routes_segs.get(t.route_id)
        if r is None:
            r = {}
            routes_segs[t.route_id] = r
        s = r.get(t.segment_id)
        if s is None:
            routes_segs[t.route_id][t.segment_id] = {
                'c': 1,
                'r': t.route_id, 
                'o': t.route_sort_order,
                'factor': 0,
                'id': t.segment_id, 'seg': t.stop_segment,
                'rels': []
            }
        else:
            routes_segs[t.route_id][t.segment_id]['c'] += 1

    for r in routes_segs.values():
        for rr in routes_segs.values():
            for k, v in r.items():
                for kk, vv in rr.items():
                #import pdb; pdb.set_trace() 
                    if k == kk:
                        if v['o'] > vv['o']:
                            v['factor'] += 1
                        v['rels'].append(v)
    return routes_segs


class SegmentRoutes(Base, PatternBase):
    __tablename__ = 'seg_routes'

    route_id = Column(String(255), index=True, nullable=False)
    segment_id = Column(String(255), index=True, nullable=False)

    def __init__(self, route_id, segment_id, geom):
        super(SegmentRoutes, self).__init__()
        self.id = route_id + "-" + segment_id
        self.route_id = route_id
        self.segment_id = segment_id
        self.geom = geom

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
    def load(cls, session, types=['TRAM']):
        """
        build new route geometries based on segments between stops
        adjust offsets of these segments
        """
        from .segment_trips import SegmentTrips

        routes_segs = {}
        #import pdb; pdb.set_trace() 
        trips = session.query(SegmentTrips).filter(SegmentTrips.mode.in_(types))
        routes_segs = etl(trips)

        ''' ''
        for k,v in routes_segs.items():
            print("ROUTE {}".format(k))
            for vv in v.values():
                if len(vv['rels']) > 1:
                    print(vv['id'])
                    for n in vv['rels']:
                        print(n['r'], getOffsetAmounts(n['factor'], n['seg'].direction), n['seg'].bearing)
                    print()
            print(); print()
        '' '''
        SegmentRoutes.clear_tables(session)
        for r in routes_segs.values():
            for z in r.values():
                geom = z['seg'].geom
                if z['factor'] > 0 and len(z['rels']) > 1:
                    off = getOffsetAmounts(z['factor'], z['seg'].direction)
                    geom = offsetGeom(session, geom, off[0], off[1])
                route = SegmentRoutes(z['r'], z['id'], geom)
                session.add(route)
            session.commit()
        session.flush()

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

