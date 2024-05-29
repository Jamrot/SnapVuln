import config
from pydriller import Git
from icecream import ic
import logging

logger = logging.getLogger(__name__)

class PatchAnalyzer:
    """A class to analyze patches from a Git repository.

    Attributes:
        url (str): The URL of the Git repository.
        commit_id (str): The commit ID to analyze.
        repo (Git): The Git repository instance.
        commit (Commit): The specified commit instance.
    """
    def __init__(self, url, commit_id):
        """Initializes PatchAnalyzer with a repository URL and commit ID.

        Parameters:
            url (str): The URL of the Git repository.
            commit_id (str): The commit ID to analyze.
        """
        self.url = url
        self.commit_id = commit_id
        self.repo = Git(self.url)
        self.commit = self.repo.get_commit(self.commit_id)

    def get_title(self)->str:
        commit = self.commit
        title = commit.msg.splitlines()[0]
        return title

    def get_author_and_date(self)->tuple:
        commit = self.commit
        return commit.author, commit.author_date

    def get_description(self, desc_tags_prefixes:list=config.desc_tags_prefixes)->tuple:
        """Gets the full and cleaned description of the commit message.

        Parameters:
            desc_tags_prefixes (list): Prefixes to filter out description tags.

        Returns:
            tuple: full & clean commit message.
        """
        commit = self.commit
        lines = commit.msg.splitlines()
        lines_filter = list(
            filter(lambda x: not x.startswith(tuple(desc_tags_prefixes)), lines))
        clean_msg = "\n".join(lines_filter)
        return commit.msg, clean_msg

    def get_version(self)->tuple:
        commit = self.commit
        version_old = commit.parents[0] if commit.parents else None
        version_new = commit.hash
        return version_old, version_new
    
    def get_commit_info(self)->dict:
        """Gets detailed information about the commit, including version, modified files, and changed methods.

        Returns:
            dict: Commit information with the following keys:
            - version: {'old': str, 'new': str}
            - files: [{
                - 'file_path': {'old': str, 'new': str}, 
                - 'file_code': {'old': str, 'new': str}, 
                - 'functions': [{
                    - 'func_name': str, 
                    - 'func_line': {'start': int, 'end': int}, 
                    - 'func_code': {'old': str, 'new': str}, 
                    - 'func_stmt': {'added': [{'line': int, 'code': str}], 
                    - 'deleted': [{'line': int, 'code': str}]}}]}]
        """
        commit = self.commit
        commit_info = {}        

        version_old, version_new = self.get_version()
        commit_info = {
            'version': {'old': version_old, 'new': version_new},
            'files': []
        }

        modified_file = commit.modified_files
        for file in modified_file:
            # file_info = {}
            file_path_old, file_path_new = self.get_file_path(file)
            file_code_old, file_code_new = self.get_file_code(file)
            file_info = {
                'file_path': {'old': file_path_old, 'new': file_path_new},
                'file_code': {'old': file_code_old, 'new': file_code_new},
                'functions': []
            }
            for method in file.changed_methods:
                # func_info = {}
                func_name = self.get_func_name(method)
                func_code_old, func_code_new = self.get_func_code(method, file)
                added_stmt, deleted_stmt = self._get_func_stmt(file, method)
                func_info = {
                    'func_name': func_name,
                    'func_line': {'start': method.start_line, 'end': method.end_line},
                    'func_code': {'old': func_code_old, 'new': func_code_new},
                    'func_stmt': {'added': added_stmt, 'deleted': deleted_stmt}
                }
                file_info['functions'].append(func_info)

            commit_info['files'].append(file_info)        
        
        return {self.commit_id: commit_info}
    
    def get_file_path(self, file):
        file_path_new = file.new_path
        file_path_old = file.old_path
        return file_path_old, file_path_new


    def get_file_code(self, file):
        src_code_new = file.source_code
        src_code_old = file.source_code_before        
        return src_code_old, src_code_new


    def get_func_name(self, method):
        method_name = method.name
        return method_name
    

    def get_func_code(self, method:object, file:object)->tuple:
        """Gets old & new source code of the method in file.
        """
        method_before = list(filter(lambda x: x.name==method.name, file.methods_before))
        if not method_before:
            return '', ''
        method_before = method_before[0] # choose the first modified method

        src_code = file.source_code
        src_code_before = file.source_code_before

        func_code_new = self.__get_func_code_from_src(src_code, method)
        func_code_old = self.__get_func_code_from_src(src_code_before, method_before)

        return func_code_old, func_code_new


    def _get_func_stmt(self, file:object, method:object)->tuple:
        """Gets added & deleted statements of the method in file.
        """
        diff_parsed = file.diff_parsed
        func_start_line = method.start_line
        func_end_line = method.end_line
        # diff_parsed: {'added': [(lineNum, code)], 'deleted': [(lineNum, code)], 'file_path_new': path, 'file_path_old': path}
        added_stmt = diff_parsed['added'] if 'added' in diff_parsed else []
        deleted_stmt = diff_parsed['deleted'] if 'deleted' in diff_parsed else []
        func_added_stmt = []
        func_deleted_stmt = []
        for stmt in added_stmt:
            if stmt[0] >= func_start_line and stmt[0] <= func_end_line: # find the added stmt in the function
                func_added_stmt.append({
                    'line': stmt[0],
                    'code': stmt[1]                
                })
        for stmt in deleted_stmt:
            if stmt[0] >= func_start_line and stmt[0] <= func_end_line:
                func_deleted_stmt.append({
                    'line': stmt[0],
                    'code': stmt[1]
                })

        return func_added_stmt, func_deleted_stmt


    def get_parsed_diff_code(self):
        """Gets parsed diff of the modified files.

        Returns:
            list: [{'added': [(lineNum, code)], 'deleted': [(lineNum, code)], 'file_path_new': path, 'file_path_old': path}]
        """
        diff_code = []
        commit = self.repo.get_commit(self.commit_id)
        for mod_files in commit.modified_files:
            diff_code.append(mod_files.diff_parsed)
        return diff_code


    def __get_func_code_from_src(self, source_code:str, method:object)->str:
        """Extracts method source code from given file source_code.
        """
        source_code = source_code.split('\n')
        func_code = '\n'.join(source_code[method.start_line - 1:method.end_line])
        return func_code


def test():
    url = config.LINUX
    hash_id = "97bf6f81b29a8efaf5d0983251a7450e5794370d"
    patch_analyzer = PatchAnalyzer(url, hash_id)
    info = patch_analyzer.get_commit_info()
    
    ic(info['files'][0][''])


if __name__=="__main__":
    test()
