
import logging
import collections
import collections.abc
try:
    import geoip2.database
    import geoip2.models
    import geoip2.errors
except ImportError:
    geoip2 = None

if geoip2:
    GEOIP_EMPTY_COUNTRY = geoip2.models.Country({})
    GEOIP_EMPTY_CITY = geoip2.models.City({})
try:
    import maxminddb
except ImportError:
    maxminddb = None

from ..utils.func import filter_kwargs, lazy_property
from ..conf import config

_logger = logging.getLogger(__name__)

# =========================================================
# GeoIP
# =========================================================
class GeoIP(collections.abc.Mapping):
    """
    Ip Geolocalization utility, determine information such as the
    country or the timezone of the user based on their IP Address.

    The instances share the same API as `:class:`geoip2.models.City`
    <https://geoip2.readthedocs.io/en/latest/#geoip2.models.City>`_.

    When the IP couldn't be geolocalized (missing database, bad address)
    then an empty object is returned. This empty object can be used like
    a regular one with the exception that all info are set None.

    :param str ip: The IP Address to geo-localize

    .. note:

        The geoip info the the current request are available at
        :attr:`~odoo.http.request.geoip`.

    .. code-block:

        >>> GeoIP('127.0.0.1').country.iso_code
        >>> odoo_ip = socket.gethostbyname('odoo.com')
        >>> GeoIP(odoo_ip).country.iso_code
        'FR'
    """

    def __init__(self, ip, root):
        self.ip = ip
        self.root = root

    @lazy_property
    def _city_record(self):
        try:
            return self.root.geoip_city_db.city(self.ip)
        except (OSError, maxminddb.InvalidDatabaseError):
            return GEOIP_EMPTY_CITY
        except geoip2.errors.AddressNotFoundError:
            return GEOIP_EMPTY_CITY

    @lazy_property
    def _country_record(self):
        if '_city_record' in vars(self):
            # the City class inherits from the Country class and the
            # city record is in cache already, save a geolocalization
            return self._city_record
        try:
            return self.root.geoip_country_db.country(self.ip)
        except (OSError, maxminddb.InvalidDatabaseError):
            return self._city_record
        except geoip2.errors.AddressNotFoundError:
            return GEOIP_EMPTY_COUNTRY

    @property
    def country_name(self):
        return self.country.name or self.continent.name

    @property
    def country_code(self):
        return self.country.iso_code or self.continent.code

    def __getattr__(self, attr):
        # Be smart and determine whether the attribute exists on the
        # country object or on the city object.
        if hasattr(GEOIP_EMPTY_COUNTRY, attr):
            return getattr(self._country_record, attr)
        if hasattr(GEOIP_EMPTY_CITY, attr):
            return getattr(self._city_record, attr)
        raise AttributeError(f"{self} has no attribute {attr!r}")

    def __bool__(self):
        return self.country_name is not None

    # Old dict API, undocumented for now, will be deprecated some day
    def __getitem__(self, item):
        if item == 'country_name':
            return self.country_name

        if item == 'country_code':
            return self.country_code

        if item == 'city':
            return self.city.name

        if item == 'latitude':
            return self.location.latitude

        if item == 'longitude':
            return self.location.longitude

        if item == 'region':
            return self.subdivisions[0].iso_code if self.subdivisions else None

        if item == 'time_zone':
            return self.location.time_zone

        raise KeyError(item)

    def __iter__(self):
        raise NotImplementedError("The dictionnary GeoIP API is deprecated.")

    def __len__(self):
        raise NotImplementedError("The dictionnary GeoIP API is deprecated.")