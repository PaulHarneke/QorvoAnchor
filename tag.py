from uci import Client, Status, Gid, OidRanging, RangingData, App, SessionType
import time, sys

def main():

    #if len(sys.argv) < 2:
    #    print("Usage: python anchor_multi.py <port>")
    #    sys.exit(1)

    #port = sys.argv[1]
    port = "COM13"

    # Controller MAC-Adressen
    controller_macs = [0x10, 0x11, 0x12]
    session_ids = [1, 2, 3]

    # Queue für Session-Handles
    sessions = {}

    # Callback für Ranging-Daten
    def show_range(payload):
        try:
            data = RangingData(payload)
            if data.n_meas > 0:
                dist = data.meas[0].distance
                print(f"[Session {data.session_handle}] Distance: {dist:.2f} cm")
        except Exception as e:
            print(f"Decode error: {e}")

    notif_handlers = {
        (Gid.Ranging, OidRanging.Start): show_range
    }

    client = Client(port=port, notif_handlers=notif_handlers)

    # Optional: Reset Gerät, um alte Sessions zu löschen
    try:
        client.reset()
        time.sleep(1)
    except Exception:
        pass

    # Initialisiere alle Sessions nacheinander
    for sess_id, ctrl_mac in zip(session_ids, controller_macs):
        try:
            rts, session_handle = client.session_init(sess_id, SessionType.Ranging)
            if rts != Status.Ok:
                print(f"Session {sess_id} init failed: {rts}")
                continue

            if sess_id == 1:
                inputchannel=5
            else:
                inputchannel=9

            configs = [
                (App.DeviceType, 0),  # Controlee
                (App.DeviceRole, 0),
                (App.DeviceMacAddress, 0x01),
                (App.DstMacAddress, [ctrl_mac]),
                (App.MultiNodeMode, 0),
                (App.ScheduleMode, 1),
                (App.RangingRoundUsage, 2),
                (App.ChannelNumber, inputchannel),
                (App.RangingInterval, 400),
            ]

            rts, _ = client.session_set_app_config(session_handle, configs)
            if rts != Status.Ok:
                print(f"Session {sess_id} config failed: {rts}")
                continue

            rts = client.ranging_start(session_handle)
            if rts != Status.Ok:
                print(f"Session {sess_id} ranging_start failed: {rts}")
                continue

            sessions[sess_id] = session_handle
            print(f"Started session {sess_id} for controller MAC 0x{ctrl_mac:X}")
            time.sleep(0.5)  # Warte kurz, um Timeouts zu vermeiden

        except Exception as e:
            print(f"Error initializing session {sess_id}: {e}")

    print("Anchor ready. Press Ctrl+C to stop.")

    # Endlosschleife für Live-Daten
    try:
        while True:         #Automatik
           time.sleep(1)
        #time.sleep(10)     #Abbruch nach Zeit
    except KeyboardInterrupt:
        print("\nStopping all sessions...")
    finally:
        for sess_id, handle in sessions.items():
            try:
                client.ranging_stop(handle)
            except Exception as e:
                print(f"Error stopping ranging for session {sess_id}: {e}")
            try:
                client.session_deinit(handle)
                print(f"Session {sess_id} deinitialized.")
            except Exception as e:
                print(f"Error deinitializing session {sess_id}: {e}")

        try:
            client.close()
            print("All sessions closed. Exiting.")
        except Exception as e:
            print(f"Error closing client: {e}")

if __name__ == "__main__":
    main()
