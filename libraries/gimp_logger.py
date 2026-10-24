#!/usr/bin/env python
# -*- coding: utf-8 -*-
# filename: gimp_logger.py

import sys
import os
import ConfigParser
from datetime import datetime

plugin_dir = os.path.dirname( os.path.abspath( __file__ ) ).replace( "\\","/" )
config_path = os.path.normpath( os.path.join( plugin_dir, "../configs/gimp_logger.ini" ) ).replace( "\\", "/" )

class TimestampedStream( object ):
    def __init__( self, target_file ):
        self.target_file = target_file
        self.new_line = True

    def write( self, data ):
        if not data:
            return

        # Split data by lines to ensure timestamps attach strictly to new lines
        lines = data.split( '\n' )
        for i, line in enumerate( lines ):
            # If it's a continuing chunk on a fresh line, insert the stamp
            if self.new_line and line != '':
                timestamp = "[" + datetime.now().strftime( "%Y-%m-%d %H:%M:%S.%f" )[ :23 ] + "] "
                self.target_file.write( timestamp )
                self.new_line = False

            self.target_file.write( line )

            # If this isn't the final element, a newline split occurred
            if i < len( lines ) - 1:
                self.target_file.write( '\n' )
                self.new_line = True

        self.target_file.flush()

    def flush(self):
        self.target_file.flush()

class DualErrorWriter( object ):
    def __init__( self, error_path, error_mode, timestamped_master_stream ):
        self.error_path = error_path
        self.error_mode = error_mode
        self.error_file = None
        self.master_stream = timestamped_master_stream

    def write( self, data ):
        if not data:
            return

        # Create the error log only when something is written to stderr.
        if self.error_file is None:
            self.error_file = open( self.error_path, self.error_mode )

        self.error_file.write( data )
        self.error_file.flush()

        # Also include the error in the timestamped master log.
        self.master_stream.write( data )

def get_plugin_name( plugin=None ):
    if plugin and isinstance( plugin, basestring ) and plugin.strip():
        return plugin.strip()

    try:
        frame = sys._getframe( 1 )
        while frame:
            caller_file = frame.f_globals.get( "__file__" )
            if caller_file and os.path.abspath( caller_file ) != os.path.abspath( __file__ ):
                return os.path.basename( caller_file )
            frame = frame.f_back
    except Exception:
        raise

    return None

def get_gimp_ver():
    global gimp_ver

    if "/gimp/" in plugin_dir.lower():
        gimp_ver = plugin_dir.lower().split( "/gimp/" )[ 1 ].split( "/" )[ 0 ]
    else:
        if plugin_name:
            calling_file = 'GIMP plugin, "' + plugin_name + '",'
        else:
            calling_file = "An unknown GIMP plugin"
        raise Exception( calling_file + " is not in GIMP plug-ins directory." )

def get_config_option( section, option ):
    try:
        if os.path.exists( config_path ):
            config = ConfigParser.ConfigParser()
            config.read( config_path )
            if config.has_option( section, option ):
                return config.get( section, option )

    except Exception:
        raise
    return None

def get_safe_path( section, option ):
    try:
        raw_path = get_config_option(section, option)
        if raw_path:
            safe_path = raw_path.strip().strip( '"\'' ).replace( "\\", "/" ).rstrip( "/" )
            if safe_path.startswith( "." ):
                safe_path = os.path.abspath( os.path.join( plugin_dir, safe_path ) ).replace( "\\", "/" )
            return safe_path

    except Exception:
        raise
    return None

def get_full_dest_params():
    try:
        log_options = [ "FullLog", "ErrorLog" ]
        log_sections = [ "LogPaths", "LogFiles" ]
        default_paths = { "FullLog": "%GIMP_VER_DATA%/logs", "ErrorLog": "%USERDESKTOP%", }
        default_files = { "FullLog": "gimp_plugin_output.log", "ErrorLog": "gimp_plugin_error.log", }
        log_params = {}

        custom_variables = { "%SCRIPT_DIR%": plugin_dir, }

        if os.name == "nt": # "nt" means Windows
            windows_variables = {
                "%GIMP_DATA%": os.path.expandvars( "%APPDATA%/GIMP" ),
                "%GIMP_VER_DATA%": os.path.expandvars( "%APPDATA%/GIMP/" + gimp_ver ),
                "%USERDESKTOP%": os.path.expandvars( "%USERPROFILE%/Desktop" ),
                "%USERDOCS%": os.path.expandvars( "%USERPROFILE%/Documents" ),
                "%USERDLS%": os.path.expandvars( "%USERPROFILE%/Downloads" ),
            }

            custom_variables.update( windows_variables )

        elif os.name == "posix": # macOS and Linux share "posix"
            posix_variables = {
                "%USERDESKTOP%": os.path.expanduser( "~/Desktop" ),
                "%USERDOCS%": os.path.expanduser( "~/Documents" ),
                "%USERDLS%": os.path.expanduser( "~/Downloads" ),
            }

            if sys.platform == "darwin": # macOS
                mac_os_variables = {
                    "%GIMP_DATA%": os.path.expanduser( "~/Library/Application Support/GIMP" ),
                    "%GIMP_VER_DATA%": os.path.expanduser( "~/Library/Application Support/GIMP/" + gimp_ver ),
                }
                posix_variables.update( mac_os_variables )

            elif sys.platform.startswith( "linux" ): # Linux
                linux_variables = {
                    "%GIMP_DATA%": os.path.expanduser( "~/.config/GIMP" ),
                    "%GIMP_VER_DATA%": os.path.expanduser( "~/.config/GIMP/" + gimp_ver ),
                }
                posix_variables.update( linux_variables )

            custom_variables.update( posix_variables )

        for log_option in log_options:
            group_path = get_safe_path( log_sections[ 0 ], log_option ) or default_paths[ log_option ]

            for key, value in custom_variables.items():
                if key in group_path:
                    group_path = group_path.replace( key, value )

            group_path = os.path.expandvars( group_path )
            if not os.path.exists( group_path ):
                os.makedirs( group_path )

            group_file = get_config_option( log_sections[ 1 ], log_option ) or default_files[ log_option ]
            full_filename_path = os.path.join( group_path, group_file ).replace( "\\", "/" )
            log_params[ log_option ] = [ full_filename_path, get_config_option( "LogModes", log_option ) or "w" ]

        return log_params

    except Exception:
        raise
    return None

def enable_logging( plugin=None ):
    global plugin_name
    plugin_name = get_plugin_name( plugin )

    try:
        get_gimp_ver()
        log_params = get_full_dest_params()
        log_all_params = log_params[ "FullLog" ]
        log_err_params = log_params[ "ErrorLog" ]

        # Open everything_log file
        everything_log = open( log_all_params[ 0 ], log_all_params[ 1 ] )

        # Build the master timestamp pipeline
        master_timestamp_stream = TimestampedStream( everything_log )

        # Route standard print streams through the timestamp generator
        sys.stdout = master_timestamp_stream

        # Route error streams to write raw to errors log AND stamp chronologically to master log
        sys.stderr = DualErrorWriter( log_err_params[ 0 ], log_err_params[ 1 ], master_timestamp_stream )

        print( plugin_name + ": Initialization successful!" )
    except Exception:
        raise
