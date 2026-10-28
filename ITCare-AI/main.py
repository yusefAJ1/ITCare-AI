
import json
from pathlib import Path

DATA_FILE = Path(__file__).with_name("assets.json")


def load_assets():
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        print("Warning: Could not read assets.json.")
        return []


def save_assets():
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(assets, file, indent=4, ensure_ascii=False)


assets = load_assets()


def find_asset(search_term):
    search_term = search_term.strip().lower()

    for asset in assets:
        if (
            str(asset["id"]) == search_term
            or search_term in asset["name"].lower()
        ):
            return asset

    return None


def add_asset():
    print("\n--- Register a New Device ---")

    name = input("Device name: ").strip()
    device_type = input("Device type: ").strip()
    location = input("Device location: ").strip()

    if not name or not device_type or not location:
        print("All fields are required.")
        return

    next_id = max(
        (asset["id"] for asset in assets),
        default=0
    ) + 1

    asset = {
        "id": next_id,
        "name": name,
        "type": device_type,
        "location": location,
    }

    assets.append(asset)

    try:
        save_assets()
        print(f"Device #{next_id} saved successfully.")
    except OSError:
        assets.pop()
        print("Error: Could not save the device.")


def list_assets():
    print("\n--- Device Inventory ---")

    if not assets:
        print("No devices registered.")
        return

    for asset in assets:
        print(
            f"ID: {asset['id']} | "
            f"Name: {asset['name']} | "
            f"Type: {asset['type']} | "
            f"Location: {asset['location']}"
        )


def search_asset():
    term = input("Enter device ID or name: ")
    asset = find_asset(term)

    if asset:
        print("\nDevice found:")
        print(f"ID: {asset['id']}")
        print(f"Name: {asset['name']}")
        print(f"Type: {asset['type']}")
        print(f"Location: {asset['location']}")
    else:
        print("No matching device found.")


def update_asset():
    term = input("Enter the ID or name of the device to edit: ")
    asset = find_asset(term)

    if not asset:
        print("Device not found.")
        return

    print("Press Enter to keep the current value.")

    name = input(f"Name [{asset['name']}]: ").strip()
    device_type = input(f"Type [{asset['type']}]: ").strip()
    location = input(f"Location [{asset['location']}]: ").strip()

    old_values = asset.copy()

    if name:
        asset["name"] = name
    if device_type:
        asset["type"] = device_type
    if location:
        asset["location"] = location

    try:
        save_assets()
        print("Device updated successfully.")
    except OSError:
        asset.update(old_values)
        print("Error: Could not save the changes.")


def delete_asset():
    term = input("Enter the ID or name of the device to delete: ")
    asset = find_asset(term)

    if not asset:
        print("Device not found.")
        return

    print(f"Selected: {asset['name']} (ID {asset['id']})")
    confirmation = input("Type DELETE to confirm: ").strip()

    if confirmation != "DELETE":
        print("Deletion cancelled.")
        return

    assets.remove(asset)

    try:
        save_assets()
        print("Device deleted successfully.")
    except OSError:
        assets.append(asset)
        print("Error: Could not save the deletion.")


def main():
    print(f"Loaded {len(assets)} saved device(s).")

    while True:
        print("\n====== ITCare AI ======")
        print("1. Register a device")
        print("2. View all devices")
        print("3. Search for a device")
        print("4. Edit a device")
        print("5. Delete a device")
        print("6. Exit")

        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            add_asset()
        elif choice == "2":
            list_assets()
        elif choice == "3":
            search_asset()
        elif choice == "4":
            update_asset()
        elif choice == "5":
            delete_asset()
        elif choice == "6":
            print("Thank you for using ITCare AI!")
            break
        else:
            print("Invalid choice. Enter a number from 1 to 6.")


if __name__ == "__main__":
    main()
