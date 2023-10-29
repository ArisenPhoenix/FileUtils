import os
import shutil
import json


class Path:
    def __init__(self, path: str):
        if not isinstance(path, str):
            raise ValueError(f"Path: {path} Must Be Of Type 'str', it is currently of type: {type(str)}")
        self.path = path
        self.type = None
        if self.check_is_dir():
            self.type = "dir"
        elif self.check_is_file():
            self.type = "file"
        else:
            raise ValueError(f"Path Provided: '{self.path}' is not a valid file_path nor a directory")

        self.name = None
        if not self.name:
            self.name = self.path.split("/")[-1]

    def check_is_dir(self, path=None):
        if path is None:

            return os.path.isdir(self.path)
        elif isinstance(path, str):
            return os.path.isdir(path)
        else:
            raise ValueError(f"The path {path} is not a string and cannot be used.")

    def check_is_file(self):
        return os.path.isfile(self.path)

    def check_is_text(self, match_list: list):
        for text in match_list:
            if text in self.path:
                return text
        return False

    def get(self):
        if self.type == "dir":
            return Dir(self.path)
        else:
            return File(self.path)

    def get_clean_name(self):
        return self.path.split("/")[-1]

    def get_current_path(self):
        return self.path.split("/")[0:-1]

    def move(self, new_path: str):

        if self.check_is_dir() or self.check_is_file():
            return Move().move(self.path, new_path)
        if not self.check_is_dir():
            raise NotADirectoryError(f"The Path That Dir Contains: {self.path} Is Not A Valid Directory")
        elif not self.check_is_file():
            raise FileNotFoundError(f"The Path That Dir Contains: {self.path} Is Not A Valid Directory")


    def name(self):
        return self.name

    def write_file(self, filename: str, data, file_type: str, operation: str, callback=None):
        """Don't Include The File Extension In The Name. That Is Done For You."""

        if isinstance(filename, str) and isinstance(file_type, str):
            new_file_path = os.path.join(self.path, filename)
            new_file_path += f".{file_type}"
            with open(new_file_path, operation, encoding="utf-8") as file:
                if file_type == "json":
                    json.dump(data, file, ensure_ascii=False, indent=4)
                elif file_type == "txt":
                    file.write(data)
                elif callback:
                    callback(filename, data, file_type, operation, file)
                else:
                    ValueError(f"File Type {file_type} Not In The Covered Types Of Files ... Yet")
        else:
            raise ValueError(
                f"Both filename And filetype Must Be of Type 'str'\n You Provided {filename} and {file_type}")

    def make_dir(self, path: str = None):
        if isinstance(path, str):

            temp_path = os.path.join(path)
            if self.check_is_dir(temp_path):
                self.path = temp_path
                return self
            else:
                try:
                    os.mkdir(temp_path)
                    if self.check_is_dir(temp_path):
                        self.path = temp_path
                        return self
                except FileNotFoundError:
                    return self

        else:
            raise ValueError(f"The path: {path} is not a string and cannot be created.")

    def append(self, dirname: str):
        """
        Directly Appends The Dirname Provided And Does Nothing Afterward.
        """
        self.path = os.path.join(self.path, dirname)
        return self

    def __str__(self):
        return self.path

    def __repr__(self):
        return self.path


class Dir(Path):
    def __init__(self, dir_path: str):
        super().__init__(dir_path)
        self.path = dir_path
        self.is_dir = self.check_is_dir()

    def add(self, next_level: str):
        """
        Directly moves to the next path provided. If it doesn't exist, it is created.
        """
        if isinstance(next_level, str):
            temp_loc = os.path.join(self.path, next_level)
            if self.check_is_dir(temp_loc):
                self.path = temp_loc
            else:
                try:
                    os.mkdir(temp_loc)
                    self.path = temp_loc
                except FileExistsError:
                    return File(temp_loc)
                except FileNotFoundError:
                    pass
                except IsADirectoryError:
                    self.path = temp_loc
            return self.path

        else:
            raise ValueError(f"The Next Level of type: {type(next_level)} Is Not Able To Make A Directory")

    def split(self, path: str = None) -> tuple | list:
        if path is None:
            return os.path.split(self.path)
        elif isinstance(path, str):
            return os.path.split(path)
        else:
            raise ValueError(f"The path: {path} is not of type {str}")

    @staticmethod
    def join(path: list | tuple):
        # print("")
        if type(path) == list or type(path) == tuple:
            return os.path.join(*path)
        else:
            raise ValueError(f"The path: {path} is not of type {list}")

    def dig(self, new_folder_name: str):
        """Goes To The Specified Next Level 'Deeper' Directory. If It Doesn't Yet Exist, It Will..."""
        temp_folder_path = os.path.join(self.path, new_folder_name)

        if self.check_is_dir(temp_folder_path):
            self.path = temp_folder_path
        else:
            if self.check_is_dir():
                new_level = self.add(temp_folder_path)
                if self.check_is_dir(new_level):
                    self.path = new_level
        return self

    def rise(self):
        new_folder_path = self.split()[:-1]
        new_folder_path = self.join(new_folder_path)
        if self.check_is_dir(new_folder_path):
            self.path = new_folder_path
            return self
        else:
            raise NotADirectoryError("Huh That's Funny... This Isn't A Directory.")

    def move(self, new_path: str):
        if self.check_is_dir():
            if not self.check_is_dir(new_path):
                shutil.move(self.path, new_path)
                self.path = new_path
                return self
            else:
                return False

    def slide(self, folder_name):
        try:
            if len(os.listdir(self.path)) == 0:
                temp = os.path.join(self.path, folder_name)
                os.mkdir(temp)
            else:
                temp = os.path.join(self.path, folder_name)
                os.mkdir(temp)
        except FileExistsError:
            pass
        return self

    def __str__(self):
        return self.path


class File(Path):
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.path = file_path
        self.is_file = self.check_is_file()

    def make_file(self):
        if not self.is_file:
            os.mkdir(self.path)
            return True
        else:
            return False


class Move:
    def __init__(self):
        self.old_path = None
        self.new_path = None
        self.dir_path = None
        self.new_base_dir = None
        self.match_list = []
        self.file_path = None

    @staticmethod
    def move(old_path, new_path):
        shutil.move(old_path, new_path)
        return True

    def move_match(self, path: str, match_list, new_base_dir):
        path = Path(path)
        match = path.check_is_text(match_list)
        if match:
            new_path = os.path.join(new_base_dir, path.get_clean_name())
            return self.move(path, new_path)
        return False

    def move_dir(self, dirpath: str, new_base_dir, match_list=None):
        if Dir(dirpath).check_is_dir():
            if match_list:
                return self.move_match(dirpath, match_list, new_base_dir)
            else:
                return self.move(dirpath, new_base_dir)
        return False

    def move_file(self, filepath: str, new_base_dir: str, match_list: list = None):
        file = File(filepath)
        if file.is_file and type(match_list) == list:
            return self.move_match(filepath, match_list, new_base_dir)
        else:
            return self.move(filepath, new_base_dir)
