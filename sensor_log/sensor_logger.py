#!/usr/bin/env python3
import serial, time, os, datetime

PORT = "/dev/ttyACM0"
BAUD = 115200
LOG_DIR = os.path.expanduser("/home/psagro/Desktop/sensor_log")
HEADER = ("timestamp,millis,s1_nem,s1_sicaklik,s1_ec,s1_ph,"
          "s2_nem,s2_sicaklik,s2_ec,s2_ph,azot_n,fosfor_p,potasyum_k,s3_ham_adc,s3_gerilim,s3_nem\n")

def is_log_minute(now):
    t = now.hour * 60 + now.minute
    if True:          # yarım saatte bir
        return True
    if 10*60+29 <= t <= 10*60+35:      # sulama penceresi: 10:29-10:35 dakikalık
        return True
    return False

def valid_csv(line):
    parts = line.split(",")
    if len(parts) != 15:
        return False
    try:
        [float(p) for p in parts]
        return True
    except ValueError:
        return False

def write_row(row):
    now = datetime.datetime.now()
    path = os.path.join(LOG_DIR, now.strftime("%Y-%m-%d") + ".csv")
    new_file = not os.path.exists(path)
    with open(path, "a") as f:
        if new_file:
            f.write(HEADER)
        f.write(now.strftime("%Y-%m-%d %H:%M:%S") + "," + row + "\n")

def main():
    last_good = None
    last_written_minute = None
    expect_csv = False
    while True:
        try:
            with serial.Serial(PORT, BAUD, timeout=2) as ser:
                while True:
                    raw = ser.readline().decode(errors="ignore").strip()
                    if raw == "CSV:":
                        expect_csv = True
                        continue
                    if expect_csv:
                        expect_csv = False
                        if valid_csv(raw):
                            last_good = raw
                    now = datetime.datetime.now()
                    minute_key = now.strftime("%Y-%m-%d %H:%M")
                    if last_good and is_log_minute(now) and minute_key != last_written_minute:
                        write_row(last_good)
                        last_written_minute = minute_key
        except (serial.SerialException, OSError):
            time.sleep(5)  # port koparsa bekle, yeniden bağlan

if __name__ == "__main__":
    main()
