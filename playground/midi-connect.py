import mido
import time

def list_midi_ports():
    """Lists available MIDI input ports."""
    print("Available MIDI input ports:")
    # Get a list of available input port names
    input_ports = mido.get_input_names()
    if not input_ports:
        print("No MIDI input ports found. Make sure your device is connected.")
        return None
    
    # Print the ports with their index numbers
    for i, port in enumerate(input_ports):
        print(f"{i}: {port}")
    return input_ports

def main():
    """Main function to select a port and read MIDI messages."""
    available_ports = list_midi_ports()
    if not available_ports:
        return

    port_name = None
    # Automatically select the FGDP-50 if found
    for name in available_ports:
        if "FGDP-50" in name:
            port_name = name
            print(f"\nAutomatically selected FGDP-50: '{port_name}'")
            break

    # If not found automatically, ask the user
    if not port_name:
        try:
            port_index = int(input("\nEnter the number for your FGDP-50 port: "))
            if 0 <= port_index < len(available_ports):
                port_name = available_ports[port_index]
            else:
                print("Invalid number.")
                return
        except (ValueError, IndexError):
            print("Invalid input. Please enter a number from the list.")
            return

    print(f"\nListening for MIDI input from '{port_name}'... Press Ctrl+C to exit.")
    
    try:
        # Open the selected MIDI port and start reading messages
        with mido.open_input(port_name) as inport:
            for msg in inport:
                # msg is a mido message object
                if msg.type == 'clock':
                    continue
                print(msg)
                
    except KeyboardInterrupt:
        print("\nStopped listening.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()