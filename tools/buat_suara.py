# Alat bantu (bukan bagian dari game): mensintesis efek suara dan musik latar bergaya 8-bit
# lalu menyimpannya sebagai WAV ke assets/sounds/. Jalankan sekali: .venv/bin/python tools/buat_suara.py
import array
import math
import os
import wave


class ChiptuneSynth:
    """Membuat bunyi 8-bit dari gelombang kotak (square) dan segitiga (triangle)."""

    RATE = 44100
    NOTES = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3,
             "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}

    def __init__(self, out_dir):
        self._out_dir = out_dir

    # --- bahan dasar ---

    def freq(self, note):
        """'A4' -> 440.0 Hz; None berarti diam (rest)."""
        if note is None:
            return 0.0
        name, octave = note[:-1], int(note[-1])
        return 440.0 * 2 ** ((self.NOTES[name] + (octave - 4) * 12) / 12)

    @staticmethod
    def square(phase, duty=0.5):
        return 1.0 if phase % 1.0 < duty else -1.0

    @staticmethod
    def triangle(phase):
        return 4 * abs(phase % 1.0 - 0.5) - 1

    def tone(self, freq_start, seconds, volume, wave_fn, freq_end=None, fade=0.03):
        """Satu nada (bisa meluncur dari freq_start ke freq_end) dengan fade masuk/keluar agar tidak 'klik'."""
        n = int(self.RATE * seconds)
        freq_end = freq_start if freq_end is None else freq_end
        out, phase = [], 0.0
        fade_n = max(1, int(self.RATE * fade))
        for i in range(n):
            f = freq_start + (freq_end - freq_start) * i / n
            phase += f / self.RATE
            env = min(1.0, i / 200, (n - i) / fade_n)
            out.append(wave_fn(phase) * volume * env if f > 0 else 0.0)
        return out

    def sequence(self, notes, beat, volume, wave_fn):
        """notes: daftar (nada, jumlah ketukan)."""
        out = []
        for note, beats in notes:
            out += self.tone(self.freq(note), beats * beat, volume, wave_fn)
        return out

    @staticmethod
    def mix(*tracks):
        length = max(len(t) for t in tracks)
        return [sum(t[i] for t in tracks if i < len(t)) for i in range(length)]

    def save(self, name, samples):
        os.makedirs(self._out_dir, exist_ok=True)
        path = os.path.join(self._out_dir, f"{name}.wav")
        data = array.array("h", (int(max(-1.0, min(1.0, s)) * 32767) for s in samples))
        with wave.open(path, "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(self.RATE)
            f.writeframes(data.tobytes())
        print(f"Tersimpan: {path} ({len(samples) / self.RATE:.2f} dtk)")

    # --- bunyi untuk game ---

    def catch_good(self):
        duty = lambda p: self.square(p, 0.25)
        return self.tone(self.freq("E6"), 0.06, 0.35, duty) + self.tone(self.freq("A6"), 0.10, 0.35, duty)

    def catch_rotten(self):
        return self.tone(420, 0.35, 0.4, lambda p: self.square(p, 0.5), freq_end=90)

    def win(self):
        duty = lambda p: self.square(p, 0.25)
        notes = [("C5", 1), ("E5", 1), ("G5", 1), ("C6", 4)]
        return self.sequence(notes, 0.09, 0.35, duty)

    def lose(self):
        notes = [("G4", 1), ("F#4", 1), ("F4", 1), ("E4", 4)]
        return self.sequence(notes, 0.18, 0.35, lambda p: self.square(p, 0.5))

    def music(self):
        # 8 birama 4/4, tempo 140 BPM; panjangnya pas kelipatan ketukan sehingga bisa diulang tanpa jeda.
        beat = 60 / 140
        melody = [
            ("C5", 1), ("E5", 1), ("G5", 1), ("E5", 1),
            ("F5", 1), ("A5", 1), ("G5", 1), (None, 1),
            ("E5", 1), ("G5", 1), ("C6", 1), ("G5", 1),
            ("F5", 1), ("E5", 1), ("D5", 1), (None, 1),
            ("C5", 1), ("E5", 1), ("G5", 1), ("E5", 1),
            ("F5", 1), ("A5", 1), ("C6", 1), ("A5", 1),
            ("G5", 1), ("F5", 1), ("E5", 1), ("D5", 1),
            ("C5", 2), ("G4", 1), (None, 1),
        ]
        bass = [
            ("C3", 2), ("G2", 2), ("F2", 2), ("C3", 2),
            ("C3", 2), ("E3", 2), ("G2", 2), ("B2", 2),
            ("C3", 2), ("G2", 2), ("F2", 2), ("A2", 2),
            ("G2", 2), ("G2", 2), ("C3", 2), ("C3", 2),
        ]
        lead = self.sequence(melody, beat, 0.12, lambda p: self.square(p, 0.25))
        low = self.sequence(bass, beat, 0.25, self.triangle)
        return self.mix(lead, low)

    def save_all(self):
        for name in ("catch_good", "catch_rotten", "win", "lose", "music"):
            self.save(name, getattr(self, name)())


ChiptuneSynth(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "sounds")).save_all()
