# coding=utf-8
from __future__ import absolute_import


import octoprint.plugin
import octoprint.filemanager.storage
from octoprint.events import Events
import os
from datetime import datetime as dt, timedelta


class UploadpurgerPlugin(octoprint.plugin.SettingsPlugin,
                            octoprint.plugin.AssetPlugin,
                            octoprint.plugin.TemplatePlugin,
                            octoprint.plugin.EventHandlerPlugin,
                            octoprint.plugin.StartupPlugin
                            ):

    def __init__(self):
        self.monitored_events = [Events.UPLOAD, Events.STARTUP]

    def on_after_startup(self):
        pass

    def on_event(self, event, payload):
        upload_folder = self._settings.getBaseFolder("uploads")
        lfs = octoprint.filemanager.storage.LocalFileStorage(upload_folder)

        if event in self.monitored_events:
            if self._settings.get_int(["cut_off_length"]) > 0:
                self._logger.info(f"Purging uploads unused for {self._settings.get(['cut_off_length'])} days or more.")
                for k,v in lfs.list_files().items():
                    if "type" not in v or v["type"] != "machinecode":
                        continue

                    try:
                        metadata = lfs.get_metadata(v["path"])
                        self._logger.info(f"Considering file {v['path']}")
                        #self._logger.info(f"Metadata = {metadata}")

                        if "history" in metadata:
                            last_used = max(item['timestamp'] for item in metadata['history'])
                        else:
                            last_used = os.stat(os.path.join(upload_folder,v["path"])).st_mtime
 
                        last_used = dt.fromtimestamp(last_used)

                        self._logger.info(f"Last used =  {last_used}")

                        if last_used < dt.now() - timedelta(days = self._settings.get_int(["cut_off_length"])):
                            self._logger.info(f"Deleting {v['path']}.")
                            try:
                                lfs.remove_file(v["path"])
                            except OSError as error:
                                self._logger.error(f"There was an error removing the file {file}: {error}")
                    except FileNotFoundError:
                        pass

    # ~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return {
            "cut_off_length": 0
        }

    # ~~ AssetPlugin mixin

    def get_assets(self):
        return {
            "js": ["js/uploadpurger.js"]
        }

    # ~~ TemplatePlugin mixin

    def get_template_vars(self):
        return {"plugin_version": self._plugin_version}

    # ~~ Softwareupdate hook

    def get_update_information(self):
        return {
            "uploadpurger": {
                "displayName": "Upload Purger",
                "displayVersion": self._plugin_version,
                "type": "github_release",
                "user": "lexitus",
                "repo": "OctoPrint-UploadPurger",
                "current": self._plugin_version,
                "pip": "https://github.com/lexitus/OctoPrint-UploadPurger/archive/{target_version}.zip",
            }
        }


__plugin_name__ = "Upload Purger"
__plugin_pythoncompat__ = ">=3,<4"  # only python 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = UploadpurgerPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
