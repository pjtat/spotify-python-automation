from modify_data_exports import ModifyDataExports
from file_handler import FileHandler

def combine_and_clean_data():
    modify_data_exports = ModifyDataExports()
    file_handler = FileHandler()
    
    file_handler.combine_spotify_exports()
    file_handler.create_new_modified_data_file()

    modify_data_exports.remove_null_items()
    modify_data_exports.remove_ignored_items()
    modify_data_exports.remove_unneeded_data()
    modify_data_exports.rename_fields()
    modify_data_exports.clean_data()

def create_example_files():
    file_handler = FileHandler()
    
    # Pull in the modified data
    modified_data = file_handler.pull_modified_data()

    # Create example and test files of raw data
    file_handler.create_example_file(modified_data, 'combined_spotify_data_raw_example.json', 'raw')
    
    # Create example files for processed data
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