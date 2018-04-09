# **configurehue**

[![The MIT License](https://img.shields.io/badge/license-MIT-orange.svg?style=flat-square)](http://opensource.org/licenses/MIT)

> Configuration management for Hue bridges.

Use *configurehue* to manage IP addresses and usernames for Hue bridges.  More
to come.

## Development

The intention is for *configurehue* to provide three moddable interfaces or layers
 to allow for integration into any application.  Presently these are implemented
 as three base classes.  The 'modding' is then simply subclassing them and providing
 the missing methods.

### User Interface Layer

``` python
class InterfaceLayer(object):
class ConsoleInterface(InterfaceLayer):
class KivyInterface(InterfaceLayer):
```

Grossly oversimplified to merely handle request for bridge link request and feedback.
 Needs expansion to include listing multiple known bridges and 'last used' information
 for usernames.

### Bridge Interface Layer

``` python
class BridgeLayer(object):
class UrllibBridge(BridgeLayer):
class QhueBridge(BridgeLayer):
```

Meant to handle interactions with the bridge itself, specifically validating, creating
 and deleting usernames.  The generic example uses the Python standard urllib.  Additional
 examples could include usings 'requests' in place of urllib.  Alternatively, an
 application developer may prefer to use facilities provided by the broader hue api
 that they're using.

### Storage Interface Layer

``` python
class StorageLayer(object):
class JSONStorage(StorageLayer):
class CWDStorage(StorageLayer):
```

The base class utilizes an internal structure comparable to the layout of the
 'get configuration' command.  Therefore, it's assumed to be serializable and the
 basic subclass example uses JSON and handles the file system interaction.  The intent
 is to provide enough virtualization that an application-wide configuration manager
 could be hooked in.

## Contributions

Welcome at <https://github.com/Overboard/configurehue>

## Status

Planning, Alpha.
