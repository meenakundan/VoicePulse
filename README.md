VoicePulse is to measure heart rate from the voice of patient. pateint should make a sound of vowels(make sound of I for better accuracy).

VoicePulse is a real-time Python-based system for measuring heart rate from vocal sounds, particularly vowels, with 84% accuracy, enabling continuous monitoring. Key features were extracted from vowel sounds using Hamming windowing and FFT. A linear relationship between heart rate and FFT-derived features was established, identifying relevant coefficients. A speech processing approach was employed to achieve the most accurate correlation between voice and heart rate.

Steps:
1. after runnig the script click the "record audio" button and make the sound of any vowel (make sound of I for better accuracy) for the duration that we have decided(minimum duration should be 3 sec).
![Screenshot 2024-08-30 021935](https://github.com/user-attachments/assets/875d5e23-fd84-4f34-9895-4b334dd7a90d)


2. click the button "process audio" to know your heart beat.
   ![Screenshot 2024-08-30 022005](https://github.com/user-attachments/assets/a483007c-bade-4e78-9a5f-df8d331fab79)

3. if there is no voice detected then it will show the no speech detected.
   ![Screenshot 2024-08-30 022040](https://github.com/user-attachments/assets/8d516af9-724a-486b-9469-62fe184dac65)
