# Seismic Fractal Dimension Calculator 🌍

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://seismic-fractal-dimension-calculator.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)

🔗 **Online Demo**: [https://seismic-fractal-dimension-calculator.streamlit.app/](https://seismic-fractal-dimension-calculator.streamlit.app/)

---

## 🌟 Χαρακτηριστικά

- Υποστήριξη μορφών αρχείων: **SAC, MSEED**.
- Προεπεξεργασία σημάτων: Detrending (none/linear/demean), φιλτράρισμα (lowpass/highpass/bandpass).
- Απεικόνιση αποτελεσμάτων με διαγράμματα και R² score.
- Δυνατότητα λήψης γραφημάτων ως PNG.

---

## ⚙️ Εγκατάσταση

1. Κλωνοποιήστε το repository:
   ```bash
   git clone https://github.com/GiannisBab/Seismic-Fractal-Dimension-Calculator.git
   ```
2. Εγκαταστήστε τις απαιτούμενες βιβλιοθήκες:
   ```bash
   pip install -r requirements.txt
   ```
3. Μεταβείτε στον φάκελο:
   ```bash
   cd Seismic-Fractal-Dimension-Calculator
   ```
4. Εκκινήστε την εφαρμογή:
   ```bash
   streamlit run app.py
   ```

---

## 🛠️ Χρήση

1. **Μεταφορτώστε ένα σεισμογραφικό αρχείο** (ή χρησιμοποιήστε το [παράδειγμα EVGI](example/EVGI)).
2. **Ρυθμίστε τις παραμέτρους προεπεξεργασίας μέσω της διεπαφής.** (Προαιρετικό)
3. **Πατήστε **Calculate Fractal Dimension**.**
4. **Κατεβάστε τα αποτελέσματα ως εικόνα PNG.**

---

## 🖼️ Στιγμιότυπα Οθόνης

### Αρχική Οθόνη
<img src="screenshots/1.png" alt="Αρχική Οθόνη" width="80%">

### Προεπισκόπηση Σεισμογραφικών Δεδομένων
<img src="screenshots/2.png" alt="Προεπισκόπηση Δεδομένων" width="80%">

### Αποτελέσματα Υπολογισμού
<img src="screenshots/3.png" alt="Αποτελέσματα" width="80%">

---

🙋 **Ερωτήσεις ή προτάσεις**;  
Ανοίξτε ένα [issue](https://github.com/GiannisBab/Seismic-Fractal-Dimension-Calculator/issues) ή επικοινωνήστε μέσω [GitHub Discussions](https://github.com/GiannisBab/Seismic-Fractal-Dimension-Calculator/discussions).
