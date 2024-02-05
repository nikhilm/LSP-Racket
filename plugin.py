import sublime, sublime_plugin

from LSP.plugin import AbstractPlugin, register_plugin, unregister_plugin, Request

SESSION_NAME = "Racket"


class LspRacket(AbstractPlugin):
    @classmethod
    def name(cls) -> str:
        return SESSION_NAME

    def on_pre_server_command(self, command, done_callback):
        print("Pre server called", command)
        if command["command"] == "racket":
            session = self.weaksession()
            if not session:
                return False

            def handle_response(response):
                print("Response", response)
                # TODO: Handle errors.
                window = sublime.active_window()
                view = window.create_output_panel("LSP-racket")
                window.run_command("show_panel", {"panel": "output.LSP-racket"})
                view.run_command("lsp_racket_output", {"response": response})
                done_callback()

            session.send_request(
                Request("workspace/executeCommand", command, progress=True),
                handle_response,
                handle_response,
            )
            return True
        return False


class LspRacketOutputCommand(sublime_plugin.TextCommand):
    def run(self, edit, response):
        self.view.settings().set("auto_indent", False)
        self.view.assign_syntax("Packages/Text/Plain text.tmLanguage")
        self.view.set_read_only(False)
        self.view.insert(edit, self.view.size(), response["result"])
        self.view.set_read_only(True)


def plugin_loaded():
    register_plugin(LspRacket)


def plugin_unloaded():
    unregister_plugin(LspRacket)
