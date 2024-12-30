from modify_data_exports import ModifyDataExports
from file_handler import FileHandler

def combine_and_clean_data():
    modify_data_exports = ModifyDataExports()
    file_handler = FileHandler()
    
    print("Combining data...")
    file_handler.combine_spotify_exports()
    print("Creating new modified data file...")
    file_handler.create_new_modified_data_file()
    
    print("Removing null items...")
    modify_data_exports.remove_null_items()
    print("Removing ignored items...")
    modify_data_exports.remove_ignored_items()
    print("Removing unneeded data...")
    modify_data_exports.remove_unneeded_data()
    print("Renaming fields...")
    modify_data_exports.rename_fields()
    print("Cleaning data...")
    modify_data_exports.clean_data()

def create_example_files():
    file_handler = FileHandler()
    
    # Pull in the raw data
    raw_data = file_handler.pull_raw_data()

    # Create example and test files for raw data
    file_handler.create_example_file(raw_data, 'combined_spotify_data_raw_example.json', 'raw')
    file_handler.create_test_file(raw_data, 'combined_spotify_data_raw_test.json')
    
    # Pull in the modified data
    modified_data = file_handler.pull_modified_data()

    # Create example and test files for processed data
    modified_data = file_handler.pull_modified_data()
    file_handler.create_example_file(modified_data, 'combined_spotify_data_modified_example.json', 'processed')
    file_handler.create_test_file(modified_data, 'combined_spotify_data_modified_test.json')

def display_menu():
    print("\nSpotify Data Processing Menu:")
    print("1. Combine and Clean Data")
    print("2. Create Example / Test Files")
    print("3. Run All Operations")
    print("4. Exit")
    return input("Enter your choice (1-4): ")

def main():
    while True:
        choice = display_menu()
        
        if choice == '1':
            combine_and_clean_data()
        elif choice == '2':
            create_example_files()
        elif choice == '3':
            combine_and_clean_data()
            create_example_files()
        elif choice == '4':
            print("All Done.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()