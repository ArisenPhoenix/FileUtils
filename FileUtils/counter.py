from FileUtils.paths import Dir
import os


class Files:
    def __init__(self, root_dir):
        self.root_dir = root_dir


    def Count_Files_And_Folders(self):
        this_dir = Dir(self.root_dir)
        if this_dir.check_is_dir():
            dir_counter = 0
            file_counter = 0
            for current_dir, dir_folders, dir_files in os.walk(this_dir.path):
                dir_counter += len(dir_folders)
                file_counter += len(dir_files)

            return dir_counter, file_counter

        else:
            raise ValueError(f"The Path Provided Is Not A Directory")
