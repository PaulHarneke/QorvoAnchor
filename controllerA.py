from uci import Client, Status, Gid, OidRanging, RangingData, App, SessionType
import sys, time

def main():
    #if len(sys.argv) < 3:
    #    print("Usage: python controller.py <port> <mac_hex>")
    #    sys.exit(1)

    #port = sys.argv[1]
    port="COM4"
    #mac = int(sys.argv[2], 16)
    mac=0x10
    #session_id = mac - 0x0F  # ergibt 1,2,3 (z. B. MAC=0x10 → Session 1)
    session_id = 1

    def show_range(payload):
        try:
            data = RangingData(payload)
            if data.n_meas > 0:
                dist = data.meas[0].distance
                #print(f"{dist:.2f} cm")
                print(dist / 100)
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

    rts, session_handle = client.session_init(session_id, SessionType.Ranging)
    if rts != Status.Ok:
        print(f"session_init failed: {rts}")
        sys.exit(1)

    # Zeit- und Kanalplanung für drei Controller:
    # - Controller A (dieses Skript) nutzt Kanal 5 und startet ohne Verzögerung.
    # - Controller B nutzt Kanal 9 und startet mit 33 ms Verzögerung.
    # - Controller C nutzt Kanal 13 und startet mit 66 ms Verzögerung.
    # Alle Controller arbeiten mit einem Ranging-Intervall von 100 ms, sodass die
    # Slots gleichmäßig über eine 100 ms-Periode verteilt sind und sich nicht
    # überlappen.

    configs = [
        (App.DeviceType, 1),
        (App.DeviceRole, 1),
        (App.DeviceMacAddress, mac),
        (App.DstMacAddress, [0x01]),  # Anchor MAC
        (App.MultiNodeMode, 0),
        (App.ScheduleMode, 1),
        (App.RangingRoundUsage, 2),
        (App.ChannelNumber, 5),
        (App.RangingInterval, 100),
    ]

    rts, _ = client.session_set_app_config(session_handle, configs)
    if rts != Status.Ok:
        print(f"session_set_app_config failed: {rts}")
        sys.exit(1)

    # Controller A startet ohne Verzögerung.
    rts = client.ranging_start(session_handle)
    if rts != Status.Ok:
        print(f"ranging_start failed: {rts}")
        sys.exit(1)

    print(f"Controller {hex(mac)} started (session {session_id}). Press Ctrl+C to stop.")

    try:
        while True:         #Automatik
           time.sleep(0.01)
        #time.sleep(10)     #Abbruch nach Zeit
    except KeyboardInterrupt:
        print("Stopping...")
        client.ranging_stop(session_handle)
        client.session_deinit(session_handle)
        client.close()
    finally:
        print("Stopping...")
        client.ranging_stop(session_handle)
        client.session_deinit(session_handle)
        client.close()
if __name__ == "__main__":
    main()
