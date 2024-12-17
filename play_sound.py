import simpleaudio as sa

sound_wave = sa.WaveObject.from_wave_file(r"D:\BRAC university\CSE\CSE423\Lab1\First Program\CSE_423_PROJECT\beep.wav")
play_obj = sound_wave.play()
play_obj.wait_done()
