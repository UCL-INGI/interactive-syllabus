import os
from abc import ABC, abstractmethod
from collections import OrderedDict

from flask import safe_join

import syllabus
import yaml

from syllabus.utils.yaml_ordered_dict import OrderedDictYAMLLoader

from syllabus import get_pages_path


class ContentNotFoundError(Exception):
    pass


class Content(ABC):
    def __init__(self, path, title):
        self.path = path
        self.title = title

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, other):
        return self.path == other.path

    @property
    @abstractmethod
    def request_path(self):
        raise NotImplementedError


class Page(Content):

    def __init__(self, path, title, pages_path=None):
        pages_path = pages_path if pages_path is not None else syllabus.get_pages_path()
        # a page should be an rST file, and should have the .rst extension, for security purpose
        file_path = safe_join(pages_path, path)
        if path[-4:] != ".rst" or not os.path.isfile(file_path):
            raise ContentNotFoundError(file_path)
        super().__init__(path, title)

    def __repr__(self):
        return "Page %s" % self.path

    @property
    def request_path(self):
        if self.path[-4:] == ".rst":
            return self.path[:-4]
        return self.path


class Chapter(Content):

    def __init__(self, path, title, description=None, pages_path=None):
        pages_path = pages_path if pages_path is not None else syllabus.get_pages_path()
        file_path = safe_join(pages_path, path)
        if not os.path.isdir(file_path):
            raise ContentNotFoundError(file_path)
        super().__init__(path, title)
        self.description = description

    def __repr__(self):
        return "Chapter %s" % self.path

    @property
    def request_path(self):
        return self.path


class TableOfContent(object):
    def __init__(self, toc_file=None):
        toc_file = toc_file if toc_file is not None else safe_join(get_pages_path(), "toc.yaml")
        with open(toc_file, "r") as f:
            toc_dict = yaml.load(f, OrderedDictYAMLLoader)
            self._init_from_dict(toc_dict)

    def _init_from_dict(self, toc_dict: OrderedDict):
        self.toc_dict = toc_dict
        self.ordered_content_indices = self._get_ordered_toc(self.toc_dict)
        self.ordered_content_list = list(self.ordered_content_indices.keys())
        self.path_to_title_dict = {x.path: x.title
                                   for x in self.ordered_content_list}
        self.index = Page("index.rst", "Index")

    def __contains__(self, item):
        """
        item can be an instance of Content or the path from the pages/
        directory (excluding it in the path) to this content
        returns True if this content is in the table of content
        returns False otherwise
        """
        item = Content(item, "") if type(item) is str else item
        return item == self.index or item in self.ordered_content_indices

    def __iter__(self):
        return self.ordered_content_list.__iter__()

    def get_content_from_path(self, path):
        """
        Returns the Content object related to the given path if there is a content located at this path
        in the pages directory. If the content is a page, a Page object will be returned. Otherwise, a Chapter will be
        returned.
        Raises a ContentNotFoundError if the content does not exist in the pages directory
        or the content is not present in the Table of Contents
        """
        try:
            content = Page(path, "")
        except ContentNotFoundError:
            content = Chapter(path, "")
        if content not in self:
            raise ContentNotFoundError("The specified content in not in the Table of Contents: %s", path)
        try:
            content.title = self.path_to_title_dict[path]
        except KeyError:
            if content != self.index:
                raise Exception("no title for content at path %s" % path)
        return content

    def get_page_from_path(self, path):
        """
        Returns the Page object related to the given path if there is a page located at this path
        in the pages directory.
        Raises a ContentNotFoundError if the page does not exist in the pages directory
        or the page is not present in the Table of Contents
        """
        page = Page(path, "")
        if page not in self:
            raise ContentNotFoundError("The specified page in not in the Table of Contents")
        try:
            page.title = self.path_to_title_dict[path]
        except KeyError:
            raise Exception("no title for page at path %s" % path)
        return page

    def get_chapter_from_path(self, path):
        """
        Returns the Chapter object related to the given path if there is a chapter located at this path
        in the pages directory.
        Raises a ContentNotFoundError if the chapter does not exist in the pages directory
        or the chapter is not present in the Table of Contents
        """
        chapter = Chapter(path, "")
        if chapter not in self:
            raise ContentNotFoundError("The specified chapter in not in the Table of Contents")
        try:
            chapter.title = self.path_to_title_dict[path]
        except KeyError:
            raise Exception("no title for chapter at path %s" % path)
        return chapter

    def get_content_at_same_level(self, content):
        parent = self.get_parent_of(content)
        if parent is not None:
            return self.get_direct_content_of(parent)
        else:
            # we're at the top level
            return [self.get_content_from_path(x) for x in self.toc_dict.keys()]

    def get_next_content(self, actual_content: Content):
        """
        returns the path to the next content from this actual content.

        It will return:
        - None if actual_content is the last page of the last chapter,
        - the first page of the chapter if actual_content is a chapter,
        - the next chapter if actual_content is the last page of a chapter,
        - the next page in the same chapter otherwise
        """
        index = self.ordered_content_indices[actual_content]
        return self.ordered_content_list[index + 1] if index + 1 < len(self.ordered_content_list) else None

    def get_previous_content(self, actual_content: Content):
        """
        returns the path to the previous content from this actual content.

        It will return:
        - None if actual_content is the first page of the first chapter,
        - the last page of previous the chapter if actual_content is a chapter,
        - the chapter itself if actual_content is the first page of a chapter,
        - the previous page in the same chapter otherwise
        """
        index = self.ordered_content_indices[actual_content]
        return self.ordered_content_list[index - 1] if index > 0 else None

    def get_direct_content_of(self, content):
        """
        Returns a list containing the direct content of the given content if it is a chapter
        Returns None if it is a page
        """
        if type(content) is Page:
            return None
        chapters_list = content.path.split("/")
        toc = self.toc_dict
        # navigate in the TOC until the level of the specified chapter
        for chapter in chapters_list:
            toc = toc[chapter]["content"]
        # return the direct content
        retval = []
        for x in toc.keys():
            if "content" in toc[x]:
                retval.append(Chapter(safe_join(content.path, x), self.path_to_title_dict[safe_join(content.path, x)]))
            else:
                retval.append(Page(safe_join(content.path, x), self.path_to_title_dict[safe_join(content.path, x)]))
        return retval

    def get_containing_chapters_of(self, content):
        str_containing_chapters = content.path.split(os.sep)[:-1]
        result = []
        actual_path = []
        for chapter_str in str_containing_chapters:
            actual_path.append(chapter_str)
            joined_path = safe_join(*actual_path)
            result.append(Chapter(joined_path, self.path_to_title_dict[joined_path]))
        return result

    def get_top_level_content(self):
        res = []
        for path in self.toc_dict.keys():
            if "content" in self.toc_dict[path]:
                res.append(Chapter(path, self.path_to_title_dict[path]))
            else:
                res.append(Page(path, self.path_to_title_dict[path]))
        return res

    def get_parent_of(self, content):
        try:
            last_separator = content.path.rindex("/")
        except ValueError:
            return None
        new_path = content.path[:last_separator]
        try:
            return Chapter(new_path, self.path_to_title_dict[new_path])
        except (ContentNotFoundError, KeyError):
            return None

    @staticmethod
    def _get_ordered_toc(toc_ordered_dict, actual_path=None, actual_index=0) -> OrderedDict:
        actual_path = list() if actual_path is None else actual_path
        paths_ordered_dict = OrderedDict()
        for key, val in toc_ordered_dict.items():
            actual_path.append(key)
            title = val["title"]
            # add the path from the root until here
            if "content" in val:
                # chapter
                paths_ordered_dict[Chapter(safe_join(*actual_path), title)] = actual_index + len(paths_ordered_dict)
                # continue to explore the TOC and add the result to the paths_list
                paths_ordered_dict.update(TableOfContent._get_ordered_toc(val["content"], actual_path,
                                                                          actual_index + len(paths_ordered_dict)))
            else:
                # page
                paths_ordered_dict[Page(safe_join(*actual_path), title)] = actual_index + len(paths_ordered_dict)
            actual_path.pop()  # remove the actual chapter from the actual path as we go on to the next chapter
        return paths_ordered_dict

    @staticmethod
    def is_toc_dict_valid(toc_ordered_dict):
        """
        Returns True if the given OrderedDict represents a valid Table of Contents.
        The Table of Contents is valid of all the pages and chapters exists in the page directory.
        Returns False otherwise
        """
        try:
            TableOfContent._get_ordered_toc(toc_ordered_dict)
            return True
        except:
            return False

    def add_content_in_toc(self, content: Content):
        """ Adds the specified content at the last position of the specified containing chapter. """
        *keys, filename = content.path.split(os.sep)
        if not keys:
            # the content will be added at the top level of the ToC
            containing_chapter_dict = self.toc_dict
        else:
            containing_chapter_dict = self._traverse_toc(keys)["content"]

        if type(content) is Chapter:
            containing_chapter_dict[filename] = {"title": content.title, "content": {}}
        else:
            containing_chapter_dict[filename] = {"title": content.title}

        # recompute the other data structures of the ToC
        self._init_from_dict(self.toc_dict)

    def remove_content_from_toc(self, content: Content):
        """
        Removes the specified content from the ToC.
        Raises a KeyError is te content was already not present in the ToC.
        """
        *keys, filename = content.path.split(os.sep)
        if len(keys) > 0:
            containing_chapter = self._traverse_toc(keys)
            containing_chapter["content"].pop(filename)
        else:
            self.toc_dict.pop(filename)
        # recompute the other data structures of the ToC
        self._init_from_dict(self.toc_dict)

    def _traverse_toc(self, keys_list):
        if len(keys_list) == 0:
            return self.toc_dict
        toc = self.toc_dict[keys_list[0]]
        for key in keys_list[1:]:
            toc = toc["content"][key]
        return toc