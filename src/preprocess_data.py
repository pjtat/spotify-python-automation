import json

from modify_data_exports import ModifyDataExports

def main():
   modify_data_exports = ModifyDataExports()

   # Combine all spotify exports into one file
   modify_data_exports.combine_spotify_exports()

   # Remove tracks will null value for track, artist, AND album
   modify_data_exports.remove_null_items()

   # Remove ignored tracks, albums, and artists
   modify_data_exports.remove_ignored_items()
   
   # Remove unneeded fields and rename fields
   modify_data_exports.remove_unneeded_data()
   modify_data_exports.rename_fields()

   # Clean up data 
   modify_data_exports.clean_data()
   
if __name__ == "__main__":
    main()