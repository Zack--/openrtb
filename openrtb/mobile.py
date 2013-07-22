from decimal import Decimal

from .base import Object, Array, Field
from . import constants
from . import request


class Impression(Object):
    impid = Field(unicode, required=True)
    wseat = Field(Array(unicode))
    h = Field(int)
    w = Field(int)
    pos = Field(constants.AdPosition)
    instl = Field(int)
    btype = Field(Array(constants.BannerType))
    battr = Field(Array(constants.CreativeAttribute))


class Device(Object):
    did = Field(unicode)
    dpid = Field(unicode)
    ip = Field(unicode)
    country = Field(unicode)
    carrier = Field(unicode)
    ua = Field(unicode)
    make = Field(unicode)
    model = Field(unicode)
    os = Field(unicode)
    osv = Field(unicode)
    js = Field(int)
    loc = Field(unicode)

    connectiontype = constants.ConnectionType.CELLULAR_UNKNOWN_G
    devicetype = constants.DeviceType.MOBILE


class User(Object):
    uid = Field(unicode)
    yob = Field(int)
    gender = Field(unicode)
    zip = Field(unicode)
    country = Field(unicode)
    keywords = Field(unicode)


class Site(Object):
    sid = Field(unicode)
    name = Field(unicode)
    domain = Field(unicode)
    pid = Field(unicode)
    pub = Field(unicode)
    pdomain = Field(unicode)
    cat = Field(Array(unicode))
    keywords = Field(unicode)
    page = Field(unicode)
    ref = Field(unicode)
    search = Field(unicode)


class App(Object):
    aid = Field(unicode)
    name = Field(unicode)
    domain = Field(unicode)
    pid = Field(unicode)
    pub = Field(unicode)
    pdomain = Field(unicode)
    cat = Field(Array(unicode))
    keywords = Field(unicode)
    ver = Field(unicode)
    bundle = Field(unicode)
    paid = Field(int)


class Restrictions(Object):
    bcat = Field(Array(unicode))
    badv = Field(Array(unicode))


class BidRequest(Object):
    id = Field(unicode, required=True)
    at = Field(constants.AuctionType, default=constants.AuctionType.SECOND_PRICE)
    tmax = Field(int)
    imp = Field(Array(Impression), required=True)
    site = Field(Site, default=Site())
    app = Field(App, default=App())
    device = Field(Device, default=Device())
    user = Field(User, default=User())
    restrictions = Field(Restrictions, default=Restrictions())

    @staticmethod
    def minimal(id, imp_id):
        return BidRequest(id=id, imp=[Impression(impid=imp_id)])


class OpenRTB20Adapter(object):
    def __init__(self, brq):
        self.mobile_brq = brq
        params = {
            'id': brq.id,
            'imp': [
                request.Impression(
                    id=imp.impid,
                    banner=request.Banner(
                        w=imp.w,
                        h=imp.h,
                        pos=imp.pos,
                        battr=imp.battr,
                        btype=imp.btype,
                    ),
                    bidfloor=Decimal(0),
                ) for imp in brq.imp
            ],
            'at': brq.at,
            'tmax': brq.tmax
        }
        if brq.site:
            params['site'] = request.Site(
                id=brq.site.sid,
                name=brq.site.name,
                domain=brq.site.domain,
                publisher=request.Publisher(
                    id=brq.site.pid,
                    name=brq.site.pub,
                    domain=brq.site.pdomain
                ),
                cat=brq.site.cat,
                keywords=brq.site.keywords,
                page=brq.site.page,
                ref=brq.site.ref,
                search=brq.site.search,
            )
        if brq.app:
            params['app'] = request.App(
                id=brq.app.aid,
                name=brq.app.name,
                domain=brq.app.domain,
                publisher=request.Publisher(
                    id=brq.app.pid,
                    name=brq.app.pub,
                    pdomain=brq.app.pdomain,
                ),
                cat=brq.app.cat,
                keywords=brq.app.keywords,
                ver=brq.app.ver,
                bundle=brq.app.bundle,
                paid=brq.app.paid,
            )
        if brq.device:
            lat = lon = None
            if brq.device.loc:
                lat, lon = brq.device.split(',')
                lat, lon = float(lat), float(lon)
            params['device'] = request.Device(
                didsha1=brq.device.did,
                dpidsha1=brq.device.dpid,
                ip=brq.device.ip,
                geo=request.Geo(
                    lat=lat,
                    lon=lon,
                    country=brq.device.country,
                ),
                carrier=brq.device.carrier,
                ua=brq.device.ua,
                make=brq.device.make,
                model=brq.device.model,
                os=brq.device.os,
                osv=brq.device.osv,
                js=brq.device.js,
                connectiontype=constants.ConnectionType.CELLULAR_UNKNOWN_G,
                devicetype=constants.DeviceType.MOBILE
            )
        if brq.user:
            params['user'] = request.User(
                id=brq.user.uid,
                yob=brq.user.yob,
                gender=brq.user.gender,
                keywords=brq.user.keywords,
                geo=request.Geo(
                    country=brq.user.country,
                    zip=brq.user.zip
                )
            )
        if brq.restrictions:
            params['badv'] = brq.restrictions.badv
            params['bcat'] = brq.restrictions.bcat

        self.brq = request.BidRequest(**params)

    def __getattr__(self, k):
        return getattr(self.brq, k)

    @staticmethod
    def deserialize(data):
        brq = BidRequest.deserialize(data)

        return OpenRTB20Adapter(brq)