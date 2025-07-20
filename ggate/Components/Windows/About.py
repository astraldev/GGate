from ggate.const import Definitions
from ggate.config import APP_PREFIX, VERSION
from gi.repository import Adw

class AboutGGate:
    @staticmethod
    def create() -> Adw.AboutDialog:
        about_dialog = Adw.AboutDialog.new()
        about_dialog.set_version(VERSION)
        about_dialog.set_application_icon(APP_PREFIX)
        about_dialog.set_application_name(Definitions.app_name)
        about_dialog.set_comments(Definitions.description)
        about_dialog.set_copyright(Definitions.copyright)
        about_dialog.set_website(Definitions.website)
        about_dialog.set_license_type(Definitions.license)
        about_dialog.set_developers(Definitions.developer)
        about_dialog.set_issue_url(Definitions.devel_bug)
        about_dialog.set_comments(Definitions.description)
        about_dialog.set_developer_name(Definitions.developer_name)

        # TODO: Add support for release notes and other features
        # about_dialog.set_website()
        # about_dialog.set_release_notes()
        # about_dialog.set_support_url()
        # about_dialog.set_debug_info()
        # about_dialog.set_debug_info_filename()

        return about_dialog
