""" configurehue - configuration manager for hue bridges """


import logging
import ipaddress
from urllib.parse import urlunsplit, urlsplit, urljoin
from pathlib import Path

import discoverhue

logger = logging.getLogger(__name__)

# TODO: might interesting to subclass
# https://docs.python.org/3.6/library/urllib.parse.html?highlight=urlparse#urllib.parse.SplitResult

class BridgeURL(str):
    """ Convenient access to variations of the URL """
    def __new__(cls, urlbase, username=None, *args, **kwargs):
        if not urlbase: urlbase = ''  # Convert None to ''
        return str.__new__(cls, urlbase, *args, **kwargs)
    def __init__(self,urlbase, username=None, *args, **kwargs ):
        self.username = str(username)
        super().__init__()
    @property
    def hostname(self):
        """ Convenient access to hostname (ip) portion of the URL """
        return urlsplit(self).hostname
    @property
    def as_usr(self):
        """ Convenient access to {url}/api/{username} """
        return urljoin(self, 'api/'+self.username)
    @property
    def as_api(self):
        """ Convenient access to {url}/api/ """
        return urljoin(self, 'api')


#
# User interface abstraction
#
class InterfaceLayer(object):
    def prompt_for_button(self):
        raise NotImplementedError
    def message_not_pressed(self):
        raise NotImplementedError

class ConsoleInterface(InterfaceLayer):
    def prompt_for_button(self):
        _ = input('Press the link button on the bridge, then press ENTER')
    def message_not_pressed(self):
        print('Button must be pressed within 30 seconds of link attempt')


#
# Bridge interface abstraction
#
class BridgeLayer(object):
    def __init__(self, address):
        self.url = address
    def validate_user(self):
        # response is dict whether whitelisted or not
        # assume whitelist only returned if provided name was on it
        response_object = self.api_validate_user()
        return 'whitelist' in response_object
    def create_user(self, devicetype=None):
        if not devicetype: devicetype = construct_devicetype()
        # both success and error are returned in a list, so pop()
        response_object = self.api_create_user(devicetype).pop()
        try:
            return response_object['success']['username']
        except KeyError:
            if response_object['error']['type']==101:
                raise Exception('Press the button!')
    def delete_user(self, username):
        raise NotImplementedError
    def api_validate_user(self):
        "return decoded json"
        raise NotImplementedError
    def api_create_user(self, devicetype):
        "return decoded json"
        raise NotImplementedError

class UrllibBridge(BridgeLayer):
    def api_validate_user(self):
        import urllib.request
        import json
        url = self.url.as_usr+'/config'
        req = urllib.request.Request(url, None, method='GET')
        with urllib.request.urlopen(req) as response:
            api_response = json.loads(response.read())
        print(api_response)
        return api_response
    def api_create_user(self, devicetype):
        import urllib.request
        import json
        url = self.url.as_api
        data = json.dumps({"devicetype": devicetype})
        req = urllib.request.Request(url, data.encode('utf-8'), method='POST')
        with urllib.request.urlopen(req) as response:
            api_response = json.loads(response.read())
        print(api_response)
        return api_response

class QhueBridge(BridgeLayer):
    def api_validate_user(self):
        import qhue
        qb = qhue.Bridge(self.url.hostname, self.url.username)
        return qb.config()
    def api_create_user(self, devicetype):
        import qhue
        qb = qhue.Bridge(self.url.hostname, None)
        try:
            api_response = qb(devicetype=devicetype, http_method="post")
        except qhue.QhueException:
            # fake the response until we add exception handling in base
            api_response = [{"error": {"type": 101}}]
        return api_response


#
# Storage interface abstraction
#
class StorageLayer(object):
    def __init__(self):
        self.int_config = {}
    def __call__(self, devicetype):
        self.devicetype = devicetype
        return self
    def __enter__(self):
        self.int_config = self.load()
        self.ext_config = self.itemize_bridges(self.devicetype)
        return self.ext_config
    def __exit__(self, *exc_parms):
        self.update_bridges()
        self.dump(self.int_config)
    def itemize_bridges(self, devicetype):
        itemized_bridges = {}
        # TODO: dependency on devicetype necessary?
        # TODO: only returns one devicetype match per sn
        for sn in self.int_config:
            url = self.int_config[sn]['ipaddress']
            for username, devicedict in self.int_config[sn]['whitelist'].items():
                if devicedict["name"] == devicetype:
                    itemized_bridges[sn] = BridgeURL(url, username) 
        return itemized_bridges
    def update_bridges(self):
        # TODO: set unfound to none/null (invalidates)
        # TODO: how to handle newly discovered?
        for sn, url_info in self.ext_config.items():
            self.int_config[sn]['ipaddress'] = url_info
            # TODO: this doesn't really maintain the whitelist properly
            # specifically it doesnt remove a bad whitelist
            self.int_config[sn]['whitelist'].update({url_info.username:{'name':self.devicetype}})

    def load(self) -> dict:
        raise NotImplementedError
    def dump(self, config: dict) -> None:
        raise NotImplementedError
    # TODO: may want to add
    # def as_uri(self):
    #     raise NotImplementedError

class JSONStorage(StorageLayer):
    filename = 'hue_bridges.json'
    def __init__(self, appname='configurehue', appauthor=None):
        from appdirs import user_config_dir
        self.path = Path(user_config_dir(appname=appname, appauthor=appauthor))
        super().__init__(self)
    def load(self):
        import json
        self.path.mkdir(parents=True, exist_ok=True)
        try:
            with (self.path/self.filename).open(mode='r') as fp:
                return json.load(fp)
        except FileNotFoundError:
            return {}
    def dump(self, config):
        import json
        with (self.path/self.filename).open(mode='w') as fp:
            json.dump(config, fp, indent=4)

class CWDStorage(StorageLayer):
    filename = 'protocfg.json'
    def load(self):
        import json
        with open(self.filename, mode='r') as fp:
            result = json.load(fp)
        return result
    def dump(self, config):
        import json
        with open(self.filename, mode='w') as fp:
            json.dump(config, fp, indent=4)


# TODO: decide where to put
def construct_devicetype(appname='configurehue', devname=None):
    import socket
    if not devname: devname = socket.getfqdn()
    return appname[0:20]+'#'+devname[0:19]
    

def get(ui=ConsoleInterface()):

    devicetype = construct_devicetype()

    # ui = ConsoleInterface()
    storage = CWDStorage()

    with storage(devicetype) as bridges_in_cfg:
        previous_bridges = bridges_in_cfg.copy()  # shallow copy should be ok
        # TODO: annoyingly, discoverhue does a nop for {} rather than find all
        if previous_bridges:
            bridges_in_lan = discoverhue.find_bridges(previous_bridges)
        else:
            bridges_in_lan = discoverhue.find_bridges()

        # Replace whitelist info dropped by discoverhue
        for sn in bridges_in_lan.keys() & bridges_in_cfg.keys():
            bridges_in_lan[sn] = BridgeURL(bridges_in_lan[sn], bridges_in_cfg[sn].username)

        # Note: discovery does not return SN's not on the list, but will on find all
        for sn in bridges_in_lan.keys() - bridges_in_cfg.keys():
            bridges_in_lan[sn] = BridgeURL(bridges_in_lan[sn])
            # print('Bridges to add {}'.format(sn))

        # Nullify IP's of bridges not located
        for sn in previous_bridges:
            bridges_in_cfg[sn] = BridgeURL(None, bridges_in_cfg[sn].username)

        # TODO: better means to manage removal?
        keys_to_remove = []
        for sn, url_info in bridges_in_lan.items():
            # TODO: remove url_info from Bridge, so only one instance needed
            b = UrllibBridge(url_info)
            # if it validates then no config change and it should be returned
            # otherwise, it needs a new username and config must change
            if not b.validate_user():
                ui.prompt_for_button()
                try:
                    bridges_in_lan[sn].username = b.create_user()
                except:
                    # TODO: make a custom err
                    ui.message_not_pressed()
                    keys_to_remove.append(sn)

        # unresolved bridges should be removed from return list
        # and the usernames purged from config
        # for sn in keys_to_remove:
        #     url_info = bridges_in_lan.pop(sn)
        #     bridges_in_cfg[sn].username = None

        # remainder of changes
        bridges_in_cfg.update(bridges_in_lan)

    return bridges_in_lan

def add():
    raise NotImplementedError

def delete():
    raise NotImplementedError




if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,                                                 \
        format='%(asctime)s.%(msecs)03d %(levelname)s:%(module)s:%(funcName)s: %(message)s', \
        datefmt="%H:%M:%S")

    # QhueBridge(BridgeURL('http://192.168.0.13/',None)).create_user()

    z = get()
    print(z)
    pass
