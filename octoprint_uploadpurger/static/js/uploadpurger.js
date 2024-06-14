/*
 * View model for Upload Purger
 *
 * Based on Timelapse Purger by jneilliii
 * License: AGPLv3
 */
$(function() {
    function UploadpurgerViewModel(parameters) {
        var self = this;

        self.settingsViewModel = parameters[0];
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: UploadpurgerViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#settings_plugin_uploadpurger"]
    });
});
