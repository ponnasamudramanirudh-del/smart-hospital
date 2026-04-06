import pandas as pd

# Load doctor data
doctors = pd.read_csv("doctors.csv")

schedule = []

# Simple AI-like extractor
def extract_patient_request(message):
    message = message.lower()

    # Detect specialty
    if "cardio" in message:
        specialty = "Cardiology"
    elif "general" in message:
        specialty = "General"
    else:
        specialty = "General"

    # Detect time (numbers in sentence)
    words = message.split()
    time = None
    for word in words:
        if word.isdigit():
            time = word

    if time is None:
        time = "10"  # default

    return specialty, time


# Take input like AI
message = input("Enter your appointment request: ")

specialty, preferred_time = extract_patient_request(message)

# Schedule appointment
for idx, doctor in doctors.iterrows():
    if doctor['Specialty'] == specialty:
        slots = [s.strip() for s in doctor['AvailableSlots'].split(",")]

        if preferred_time in slots:
            time = preferred_time
            slots.remove(preferred_time)
        elif len(slots) > 0:
            time = slots[0]
            slots.pop(0)
        else:
            time = "No slot available"

        schedule.append({
            "Patient": "New Patient",
            "Doctor": doctor['Name'],
            "Time": time
        })
        break

# Show result
final_schedule = pd.DataFrame(schedule)
print(final_schedule)