#from rain_config.values import *
import values

#==============================================================================
# from rain.common.interfaces.imessenger import IMessenger
# from rain.common.interfaces.ieventrouter import IEventRouter
# from rain.dvr.interfaces.ijumpstartserver import IJumpstartServer
# from rain.dvr.interfaces.ijumpstartclient import IJumpstartClient
# from rain.dvr.interfaces.istatemgmt import IStateMgmt
# from rain.dvr.interfaces.ieventhandler import IEventHandler
# 
# from rain.common.interfaces.iconfigmanager \
#         import get_config_component_name, IConfigManager
# from rain.common.interfaces.iconfigstore import IConfigStore
# from rain.common.interfaces.itextstore import ITextStore
from interfaces.isignalhook import ISignalHook
# from rain.common.interfaces.ikvcache import IKvCache
# from rain.common.interfaces.iconfigclassifierfacility \
#         import IConfigClassifierFacility
# 
# from rain.dvr.interfaces.device.idriverdiscovery import IDriverDiscovery
# from rain.dvr.interfaces.device.idevicestorage import IDeviceStorage
# from rain.dvr.interfaces.device.ichannelstorage import IChannelStorage
from interfaces.device.ituner import ITuner
# from rain.dvr.interfaces.media.imediaarbitration import IMediaArbitration
# from rain.dvr.interfaces.client.iclientcollection import IClientCollection
# from rain.dvr.interfaces.programs.ischedule import ISchedule
#==============================================================================

from logging import getLogger
logging = getLogger(__name__)

#comp_conf_db       = get_config_component_name(values.CONF_APPCONF)
#comp_conf_device   = get_config_component_name(values.CONF_DEVICE)
#comp_conf_channels = get_config_component_name(values.CONF_CHANNELS)

_requirements = { 
#==============================================================================
#     comp_conf_db:       IConfigStore,
#     comp_conf_device:   IConfigStore,
#     comp_conf_channels: IConfigStore,
# 
# 
#     C_JUMPSTART_SERVER:  IJumpstartServer,
#     C_JUMPSTART_CLIENT:  IJumpstartClient,
#     C_MESSENGER:         IMessenger,
#     C_STATEMGMT:         IStateMgmt,
#     C_EVENTROUTER:       IEventRouter,
# 
#     C_EH_COMMAND:        IEventHandler,
#     C_EH_STATEQUERY:     IEventHandler,
#     C_EH_STATE:          IEventHandler,
#     C_EH_SYSTEM:         IEventHandler,
#     C_EH_SYSTEMQUERY:    IEventHandler,
#     C_EH_EXPERIENCE:     IEventHandler,
# 
#     
#     C_TEXT_DBCOMMENTS: ITextStore,
#     C_TEXT_BUTTONS:    ITextStore,
# 
#     C_CONFIG:               IConfigManager,
#     C_DEV_DRIVER_DISCOVERY: IDriverDiscovery,
#     C_DEV_STORAGE:          IDeviceStorage,
#     C_CHANNEL_STORAGE:      IChannelStorage,
     values.C_DEV_TUNER: ITuner,
#     C_MED_ARBITER:          IMediaArbitration,
#     
#     C_CONFIG_CLASSIFER_FACILITY_MAIN: IConfigClassifierFacility,
#     
#     C_CLIENT_CLIENTCOLLECTION: IClientCollection,
#     
     values.C_SIGNALHOOK: ISignalHook,
#     C_SDSCHEDULE: ISchedule,
#     C_KVCACHE:    IKvCache,
#==============================================================================
}

def get(name):
    try:
        return _requirements[name]
    except:
        logging.exception("No component interface requirement found with name "
                          "[%s]." % (name))
        raise

