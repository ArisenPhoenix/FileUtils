import os
import shutil
import json
from os import PathLike
import pathlib


path_type = str | PathLike

class PathNotFoundError(Exception):
    def __init__(self, path: str = "", message: str = None):
        if message is None:
            message = f"The specified path was not found: '{path}'"
        super().__init__(message)
        # self.path = path

class PathNotPathTypeError(Exception):
    def __init__(self, path: str = "", message: str = None):
        if message is None:
            message = f"{path} Must Be Of Type 'str', it is currently of type: {type(path)}"
        super().__init__(message)
        # self.path = path


class Path(PathLike):
    def __init__(self, path: path_type):  #make=False
        if not isinstance(path, path_type):
            raise PathNotPathTypeError(path)
        if isinstance(path, pathlib.Path):
            path = path.__fspath__()

        self.path = path
        self.type = None
        # self.dynamic = make
        # if not (self.is_dir or self.is_file) and make:
        #     has_ext = self.get_ext()
        #
        #     if has_ext:
        #         self.make_file(self.path)
        #     else:
        #         self.make_dir(self.path)

        if self.check_is_dir():
            self.type = "dir"
        elif self.check_is_file():
            self.type = "file"
        else:
            raise PathNotFoundError(self.path)

    def get_ext(self):
        try:
            ext = os.path.splitext(self.path)[1]
            if ext != "":
                return ext
        except IndexError as e:
            pass
        return None

    @property
    def is_dir(self):
        return os.path.isdir(self.path)

    @property
    def is_file(self):
        return os.path.isfile(self)

    def exists(self):
        return self.is_dir or self.is_file

    def check_is_dir(self, path: path_type = None):
        if path is None:
            return os.path.isdir(self.path)
        elif isinstance(path, path_type):
            return os.path.isdir(path)
        else:
            raise PathNotPathTypeError(path)

    def check_is_file(self, path: path_type = None):
        if path is None:
            return os.path.isfile(self)
        elif isinstance(path, path_type):
            return os.path.isfile(path)
        else:
            raise PathNotPathTypeError(path)

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

    def get_parent_segments(self):
        return self.path.split("/")[0:-1]

    def move(self, new_path: path_type):

        if self.check_is_dir() or self.check_is_file():
            return Move().move(self.path, new_path)
        if not self.check_is_dir():
            raise NotADirectoryError(f"The Path That Dir Contains: {self.path} Is Not A Valid Directory")
        elif not self.check_is_file():
            raise FileNotFoundError(f"The Path That Dir Contains: {self.path} Is Not A Valid Directory")
        return None

    @property
    def name(self):
        return str(os.path.basename(self.path))

    def write_file(self, filename: path_type, data, file_type: str, operation: str, callback=None):
        """Don't Include The File Extension In The Name. That Is Done For You."""
        file_type = file_type.lower()

        if (isinstance(filename, str) or isinstance(filename, PathLike)) and isinstance(file_type, str):
            new_file_path = os.path.join(self.path, filename)
            new_file_path += f".{file_type}" if file_type is not None else ""
            new_file_path = rf"{new_file_path}"

            text_types = ["json", "txt"]
            binary_types = ["jpg", "png", "gif", "pdf"]

            if file_type in text_types:
                operation = operation.replace("b", "")  # Just in case
                encoding = "utf-8"
            elif file_type in binary_types:
                operation = operation.replace("t", "") + "b"  # Force binary mode
                encoding = None
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            with open(new_file_path, operation, encoding=encoding) as file:
                if callable(callback):
                    callback(filename, data, file_type, operation, file)
                elif file_type == "json":
                    json.dump(data, file, ensure_ascii=False, indent=4)
                elif file_type == "txt":
                    file.write(data)
                elif file_type == "jpg":
                    file.write(data)
                else:
                    raise ValueError(f"Unsupported file type: {file_type}")
        else:
            raise ValueError(
                f"Both filename And filetype Must Be of Type 'str'\n You Provided {filename} and {file_type}")
        return new_file_path

    def make_file(self, path: str):
        new_path = os.path.join(self.path, path)
        if not os.path.exists(new_path):
            with open(new_path, "w") as f:
                pass

    def make(self, path = None):
        if path is None:
            path = self.path
        if not os.path.isdir(path) and not os.path.isfile(path):
            ext = self.get_ext()
            if not ext or ext == "":
                self.make_dir(path)
            else:
                self.make_file(path)


    def make_dir(self, path: path_type = None):
        if isinstance(path, path_type):

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

    def append(self, dir_name: path_type):
        """
        Directly Appends The Dirname Provided And Does Nothing Afterward.
        """
        self.path = os.path.join(self.path, dir_name)
        return self

    def __str__(self):
        return self.path

    def __repr__(self):
        return f"{self.__class__.__name__}({self.path!r})"

    def __fspath__(self):
        return self.path

    def __truediv__(self, other: path_type):
        self.make(other)
        new_path = os.path.join(self.path, other)
        if os.path.isdir(new_path):
          return Dir(new_path)
        elif os.path.isfile(new_path):
            return File(self.path)
        else:
            raise PathNotFoundError(new_path)


class Dir(Path):
    def __init__(self, dir_path: path_type):
        super().__init__(dir_path)

    @property
    def is_absolute(self):
        return os.path.isabs(self.path)

    @staticmethod
    def is_abs(path: str | Path):
        return os.path.isdir(path)

    def add(self, next_level: path_type):
        """
        Attempts to create a subdirectory with the given name.
        Fails (raises) if it already exists as a file — use `dig` for flexible traversal.
        """
        if not isinstance(next_level, path_type):
            raise ValueError(f"Expected string for next directory level, got {type(next_level)}")

        temp_loc = os.path.join(self.path, next_level)

        if self.check_is_dir(temp_loc):
            return self

        if self.check_is_file(temp_loc):
            raise FileExistsError(f"The path provided is a file: {temp_loc}")

        os.mkdir(temp_loc)
        return self

    def split(self, path: path_type = None) -> tuple | list:
        if path is None:
            return os.path.split(self.path)
        elif isinstance(path, path_type):
            return os.path.split(path)
        else:
            raise ValueError(f"The path: {path} is not of type {str}")

    @staticmethod
    def join(path: list | tuple):
        if isinstance(path, list) or isinstance(path, tuple):
            return str(os.path.join(path[0], *path[1:]))
        else:
            raise ValueError(f"{path} is not of type {list}")

    def dig(self, new_folder_name: str):
        """Goes To The Specified Next Level 'Deeper' Directory. If It Doesn't Yet Exist, It Will..."""
        temp_folder_path = os.path.join(self.path, new_folder_name)

        if self.check_is_dir(temp_folder_path):
            self.path = temp_folder_path
        else:
            if self.check_is_dir():
                new_level = self.add(temp_folder_path)
                self.path = temp_folder_path
                if new_level.is_dir:
                    self.path = new_level.path
            else:
                os.rmdir(temp_folder_path)
                raise ValueError("You dig into air.")
        return self

    def make_file(self, file_name: str):
        path = os.path.join(self, file_name)
        return Path(path)

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
        return None

    def find(self, filename):
        for file in os.listdir(self):
            if file == filename:
                return Dir(os.path.join(self, filename))
        return False

    def slide(self, folder_name):
        """
        Creates a new subdirectory under the current path with the given folder name.
        If it already exists, it won't raise an error.
        Advances self.path to that subdirectory.
        """
        new_path = os.path.join(self.path, folder_name)
        if not os.path.isdir(new_path):
            raise NotADirectoryError(f"Cannot slide into non-directory: {new_path}")
        try:
            os.mkdir(new_path)
        except FileExistsError:
            pass
        self.path = new_path
        return self

    def __truediv__(self, other: path_type):
        self.dig(other)
        if self.is_file:
            return File(self.path)
        return self



class File(Path):
    def __init__(self, file_path: path_type):
        super().__init__(file_path)

    def make_file(self):
        if not self.is_file:
            with open(self.path, "a"):
                pass
        return self




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
        if file.is_file and isinstance(match_list, list):
            return self.move_match(filepath, match_list, new_base_dir)
        else:
            return self.move(filepath, new_base_dir)
