"""Component definitions for newer, component-based singleton management."""

#==============================================================================
# from os.path import dirname
# 
# from rain_config.values import CONFIG_PATH, CONF_APPCONF, CONF_DEVICE, \
#                                CONF_CHANNELS, C_TEXT_DBCOMMENTS
# from rain_config.config_classifiers_main import classifiers_main
# 
# import rain
#==============================================================================

#==============================================================================
# # Config registry for database.
# Config_AppConfig = {
#     # Store the database config registry using JSON.
#     '_binding': 'rain.common.modules.configstore_json.ConfigStoreJson',
# 
#     # Name of registry.
#     'registry_name': CONF_APPCONF,
# 
#     # Location of configuration.
#     'config_path': CONFIG_PATH,
# }
# 
# # Config registry for the tuner.
# Config_Device = {
#     # Store the database config registry using JSON.
#     '_binding': 'rain.common.modules.configstore_sa.ConfigStoreSa',
# 
#     # Name of registry.
#     'registry_name': CONF_DEVICE,
# 
#     # Text resolver.
#     'text_component_name': C_TEXT_DBCOMMENTS,
# 
#     # Pull the connection information from another registry.
#     '_config_from': [(CONF_APPCONF, 'db', 'mysql')],
# }
# 
# # Config registry for channel information.
# Config_Channels = {
#     # Store the database config registry using JSON.
#     '_binding': 'rain.common.modules.configstore_sa.ConfigStoreSa',
# 
#     # Name of registry.
#     'registry_name': CONF_CHANNELS,
# 
#     # Pull the connection information from another registry.
#     '_config_from': [(CONF_APPCONF, 'db', 'mysql')],
# }
# 
# Jumpstart_Server = {
#     '_binding': 'rain.dvr.modules.jumpstart_server.JumpstartServer',
# }
# 
# 
# Jumpstart_Client = {
#     '_binding': 'rain.dvr.modules.jumpstart_client.JumpstartClient',
# }
# 
# Messenger = {
#     '_binding': 'rain.common.modules.messenger_rabbitmq_blocking.'
#                 'MessengerRabbitMqBlocking',
#     'hostname': 'localhost',
# }
# 
# StateMgmt = {
#     '_binding': 'rain.dvr.modules.statemgmt.StateMgmt',
# }
# 
# EventRouter = {
#     '_binding': 'rain.common.modules.event_router.EventRouter',
# }
# 
# Eh_Command = {
#     '_binding': 'rain.dvr.modules.event.eh_command.EHCommand',
# }
# 
# Eh_State = {
#     '_binding': 'rain.dvr.modules.event.eh_state.EHState',
# }
# 
# Eh_StateQuery = {
#     '_binding': 'rain.dvr.modules.event.eh_statequery.EHStateQuery',
# }
# 
# Eh_System = {
#     '_binding': 'rain.dvr.modules.event.eh_system.EHSystem',
# }
# 
# Eh_SystemQuery = {
#     '_binding': 'rain.dvr.modules.event.eh_systemquery.EHSystemQuery',
# }
# 
# Eh_Experience = {
#     '_binding': 'rain.dvr.modules.event.eh_experience.EHExperience',
# }
# 
# Text_DbComments = {
#     # Store the database config comments locally.
#     '_binding': 'rain.common.modules.text_file_library.TextFileLibrary',
#     'path': ('%s/text/db' % (dirname(rain.dvr.__file__)))
# }
# 
# Text_Buttons = {
#     # Store the database config comments locally.
#     '_binding': 'rain.common.modules.text_file_library.TextFileLibrary',
#     'path': ('%s/text/buttons' % (dirname(rain.dvr.__file__)))
# }
# 
# ConfigManager = {
#     '_binding': 'rain.common.modules.config_manager.ConfigManager',
# }
# 
# Device_Driver_Discovery = {
#     '_binding': 'rain.dvr.modules.device.driver_discovery.DriverDiscovery',
# }
# 
# Device_Storage = {
#     '_binding': 'rain.dvr.modules.device.device_storage.DeviceStorage',
# }
# 
# Channel_Storage = {
#     '_binding': 'rain.dvr.modules.device.channel_storage.ChannelStorage',
# }
#==============================================================================

Device_Tuner = {
    '_binding': 'device.tuner.Tuner',
}

#==============================================================================
# Media_Arbitration = {
#     '_binding': 'rain.dvr.modules.media.MediaArbitration',
# }
# 
# Config_ClassifierFacility_Main = {
#     '_binding': 'rain.common.modules.config_classifier_facility_static.'
#                     'ConfigClassifierFacilityStatic',
#     'type_name': 'main',
#     'child_to_parent_dict': classifiers_main,
# }
# 
# Client_ClientCollection = {
#     '_binding': 'rain.dvr.modules.client.client_collection.ClientCollection',
# }
#==============================================================================

SignalHook = {
    '_binding': 'signalhook.SignalHook',
}

#==============================================================================
# SdSchedule = {
#     '_binding': 'rain.dvr.modules.programs.schedulesdirect_schedule.'
#                     'SchedulesDirectSchedule',
# 
#     # Pull the connection information from another registry.
#     '_config_from': [#(CONF_APPCONF, 'db', 'mysql'),
#                      (CONF_APPCONF, 'schedules', 'sd')],
# }
# 
# KvCache = {
#     '_binding': 'rain.common.modules.kvcache_memcached.KvCacheMemcached',
# 
#     # Pull the connection information from another registry.
#     '_config_from': [(CONF_APPCONF, 'kvcache', 'memcached')],
# }
#==============================================================================

