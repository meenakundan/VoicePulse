import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import numpy as np
import soundfile as sf
import scipy.signal as signal
import sounddevice as sd
from scipy.signal import find_peaks, resample

# Lists to store data for accuracy calculation
oximeter_readings = []
estimated_bpms = []
absolute_errors = []

def process_audio_data(audio_data, sample_rate, oximeter_reading=None):
    print("Original sample rate:", sample_rate)

    # Ensure audio_data is in the correct shape
    audio_data = audio_data.flatten()
    print("Audio data read successfully.")

    # Desired sample rate
    desired_sample_rate = 44100

    # Resample the audio if the sample rate is not 44100 Hz
    if sample_rate != desired_sample_rate:
        number_of_samples = int(len(audio_data) * desired_sample_rate / sample_rate)
        audio_data = resample(audio_data, number_of_samples)
        sample_rate = desired_sample_rate
        print("Audio resampled to 44100 Hz.")

    # Print the final sample rate to confirm
    print("Final sample rate:", sample_rate)

    # Butterworth lowpass filter
    cutoff = 1000.0
    order = 5
    nyquist = 0.5 * sample_rate
    normal_cutoff = cutoff / nyquist
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    filtered_data = signal.lfilter(b, a, audio_data)

    # Apply Hamming window
    window = np.hamming(len(audio_data))
    windowed_data = audio_data * window

    # Compute FFT
    fft_data = np.fft.fft(windowed_data)
    fft_freqs = np.fft.fftfreq(len(windowed_data), 1 / sample_rate)
    magnitude = np.abs(fft_data)

    # Find peaks in FFT with prominence and distance
    prominence = 0.01 * np.max(magnitude)
    distance = sample_rate // 50
    peaks, properties = find_peaks(magnitude[:len(magnitude) // 2], prominence=prominence, distance=distance)
    peak_freqs = fft_freqs[peaks]
    peak_magnitudes = magnitude[peaks]

    if len(peak_freqs) >= 5:
        sorted_indices = np.argsort(peak_magnitudes)[-5:]
        most_distinguishable_peaks = peak_freqs[sorted_indices]
        most_distinguishable_peaks = np.sort(most_distinguishable_peaks)
    else:
        sorted_indices = np.argsort(peak_magnitudes)[-len(peak_freqs):]
        most_distinguishable_peaks = peak_freqs[sorted_indices]
        most_distinguishable_peaks = np.sort(most_distinguishable_peaks)

    differences = np.diff(most_distinguishable_peaks)
    avg_difference = np.mean(differences) if len(differences) > 0 else 0

    max_magnitude = np.max(magnitude)
    if max_magnitude < 20:
        print("No speech detected")
        estimated_bpm = None
    else:
        # Calculate heart rate
        estimated_bpm = 82.20 + 0.012 * avg_difference

    # Calculate absolute error
    if oximeter_reading is not None and estimated_bpm is not None:
        absolute_error = abs(estimated_bpm - oximeter_reading) / oximeter_reading
    else:
        absolute_error = None

    # Store data for accuracy calculation
    if oximeter_reading is not None:
        oximeter_readings.append(oximeter_reading)
    estimated_bpms.append(estimated_bpm)
    if absolute_error is not None:
        absolute_errors.append(absolute_error)

    # Output results
    print("Most distinguishable peak frequencies (Hz):", most_distinguishable_peaks)
    print("Differences between consecutive peaks (Hz):", differences)
    print("Average difference (Hz):", avg_difference)
    print("Estimated heart rate (bpm):", estimated_bpm)
    if oximeter_reading is not None:
        print("Oximeter reading:", oximeter_reading)
        print("Absolute error (%):", absolute_error * 100 if absolute_error is not None else None)

    return estimated_bpm, absolute_error

def record_audio(duration=5, sample_rate=44100):
    print("Recording audio...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    print("Recording complete.")
    return audio_data, sample_rate

class HeartRateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Heart Rate Estimation")

        self.canvas = tk.Canvas(root)
        self.canvas.pack(fill="both", expand=True)

        self.img = Image.open(r'C:\Users\hp\Desktop\BTPwork2\UIpage\img2.jpg')
        self.bg_img = ImageTk.PhotoImage(self.img)

        self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")

        self.duration = tk.IntVar(value=5)

        self.duration_label = ttk.Label(root, text="Recording Duration (seconds):")
        self.duration_entry = ttk.Entry(root, textvariable=self.duration)
        self.record_button = ttk.Button(root, text="Record Audio", command=self.record_audio)
        self.process_button = ttk.Button(root, text="Process Audio", command=self.process_audio)
        self.result_label = ttk.Label(root, text="", background='#0096DC')

        self.canvas.create_window(650, 300, window=self.duration_label)
        self.canvas.create_window(960, 300, window=self.duration_entry)
        self.canvas.create_window(610, 400, window=self.record_button)
        self.canvas.create_window(940, 400, window=self.process_button)
        self.canvas.create_window(700, 570, window=self.result_label)

        self.process_button.state(['disabled'])

        self.canvas.bind('<Configure>', self.resize_image)

    def resize_image(self, event):
        new_width = event.width
        new_height = event.height
        self.bg_img = ImageTk.PhotoImage(self.img.resize((new_width, new_height)))
        self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")
        self.canvas.lower("all")

    def record_audio(self):
        self.result_label.config(text="Recording....")
        self.root.update()  # Update the UI to show the "Recording...." message
        duration = self.duration.get()
        self.audio_data, self.sample_rate = record_audio(duration=duration)
        self.result_label.config(text="Audio recorded successfully.")
        self.process_button.state(['!disabled'])

    def process_audio(self):
        estimated_bpm, absolute_error = process_audio_data(self.audio_data, self.sample_rate)
        
        if estimated_bpm is None:
            result_text = "No speech detected. Please try again."
        else:
            result_text = f"Estimated BPM: {estimated_bpm}"

        self.result_label.config(text=result_text)
        # messagebox.showinfo("Processing Complete", result_text)

if __name__ == "__main__":
    root = tk.Tk()
    root.state('zoomed')  # Make the window full screen
    app = HeartRateApp(root)
    root.mainloop()
