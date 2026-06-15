from gi.repository import GObject, GLib
from ggate import Preference

# floor on playback frame interval (~60fps cap)
_PLAYBACK_MIN_INTERVAL_MS = 16
# ceiling on playback frame interval (stops few-frame circuits crawling)
_PLAYBACK_MAX_INTERVAL_MS = 200

class CircuitPlaybackAnimation(GObject.GObject):
    __gsignals__ = {
        "playback-state-changed": (GObject.SIGNAL_RUN_FIRST, None, (str,))
    }

    def __init__(self, circuit):
        GObject.GObject.__init__(self)
        self.circuit = circuit
        self.source_id = None
        self.playback_index = 0
        self.is_playing = False
        self.state = "idle"
        self.callback = None
        self.compute_error = False

    def _update_state(self, state):
        self.state = state
        self.emit("playback-state-changed", state)

    def run(self, callback):
        self.cancel()
        self.callback = callback
        self.circuit.begin_compute()
        self._update_state("computing")
        self.source_id = GLib.idle_add(self._compute_step)

    def _compute_step(self):
        if self.circuit.sim_cancelled:
            return GLib.SOURCE_REMOVE
        status, err = self.circuit.compute_slice()
        if status == "done":
            self.compute_error = err
            if self.circuit.is_animated():
                self._start_playback()
            else:
                self._finish_static()
            return GLib.SOURCE_REMOVE
        return GLib.SOURCE_CONTINUE

    def _start_playback(self):
        self.playback_index = 0
        self.is_playing = True
        self._update_state("playing")
        self.source_id = GLib.timeout_add(self._interval(), self._play_frame)

    def _play_frame(self):
        if not self.is_playing:
            return GLib.SOURCE_REMOVE
        if self.playback_index >= self.circuit.frame_count():
            self._finish()
            return GLib.SOURCE_REMOVE
        self.circuit.apply_frame_at(self.playback_index)
        self.playback_index += 1
        return GLib.SOURCE_CONTINUE

    def _finish(self):
        self.is_playing = False
        self.source_id = None
        self._update_state("ended")
        self.circuit.finalize_playback(self.compute_error, self.callback)

    def _finish_static(self):
        frame_count = self.circuit.frame_count()
        if frame_count:
            self.circuit.apply_frame_at(frame_count - 1)
        self.is_playing = False
        self.source_id = None
        self._update_state("idle")
        self.circuit.finalize_playback(self.compute_error, self.callback)

    def pause(self):
        if not self.is_playing:
            return
        if self.source_id is not None:
            GLib.source_remove(self.source_id)
            self.source_id = None
        self.is_playing = False
        self._update_state("paused")

    def play(self):
        if self.state not in ("paused", "ended"):
            return
        if self.playback_index >= self.circuit.frame_count():
            self.playback_index = 0
        self.is_playing = True
        self._update_state("playing")
        self.source_id = GLib.timeout_add(self._interval(), self._play_frame)

    def toggle_play(self):
        if self.state == "playing":
            self.pause()
        elif self.state in ("paused", "ended"):
            self.play()

    def restart(self):
        if not self.circuit.frame_count():
            return
        self.playback_index = 0
        self.circuit.apply_frame_at(0)
        if self.state != "playing":
            self.is_playing = True
            self._update_state("playing")
            self.source_id = GLib.timeout_add(self._interval(), self._play_frame)

    def seek(self, index):
        frame_count = self.circuit.frame_count()
        if not frame_count:
            return
        index = max(0, min(index, frame_count - 1))
        self.playback_index = index
        self.circuit.apply_frame_at(index)

    def stop(self):
        self.cancel()

    def cancel(self):
        if self.source_id is not None:
            GLib.source_remove(self.source_id)
            self.source_id = None
        self.circuit.cancel_compute()
        self.is_playing = False
        if self.state != "idle":
            self._update_state("idle")

    def frame_count(self):
        return self.circuit.frame_count()

    def _interval(self):
        frame_count = self.circuit.frame_count()
        return max(_PLAYBACK_MIN_INTERVAL_MS, min(int(Preference.playback_duration * 1000 / max(1, frame_count)), _PLAYBACK_MAX_INTERVAL_MS))
