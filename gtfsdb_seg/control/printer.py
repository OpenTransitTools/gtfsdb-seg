from ott.utils import string_utils

from ..model.database import Database
from ..model.database import StopSegment 


def main(cmd_name="bin/printer"):
    """ simple demo """
    from ..loader import make_args_config, make_db_url_schema

    config, args = make_args_config(cmd_name)
    url, schema = make_db_url_schema(config, args)
    is_geospatial = string_utils.get_val(args.schema, config.get('is_geospatial'))
    session = Database.make_session(url, schema, is_geospatial)
    StopSegment.print_all(session)
