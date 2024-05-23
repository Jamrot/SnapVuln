import config
from pydriller import Git
from icecream import ic


class PatchAnalyzer:
    def __init__(self, url, hash):
        self.url = url
        self.hash = hash
        self.repo = Git(self.url)
        self.commit = self.repo.get_commit(self.hash)

    def get_author_and_date(self):
        commit = self.repo.get_commit(self.hash)
        return commit.author, commit.author_date

    def get_description(self, desc_tags_prefixes):
        commit = self.repo.get_commit(self.hash)
        lines = commit.msg.splitlines()
        lines_filter = list(
            filter(lambda x: not x.startswith(tuple(desc_tags_prefixes)), lines))
        clean_msg = "\n".join(lines_filter)
        return commit.msg, clean_msg
    
    def get_file_path(self):
        commit = self.commit
        modified_files = []
        for modified_file in commit.modified_files:
            file_path_new = modified_file.new_path
            file_path_old = modified_file.old_path
            modified_files.append(
                {
                    'file_path_new': file_path_new,
                    'file_path_old': file_path_old
                }
            )
        return modified_files

    def get_file_code(self):
        pass

    def get_func_name(self):
        commit = self.commit
        func_name = []
        try:
            for file in commit.modified_files:
                for method in file.changed_methods:
                    method_name = method.name
                    file_path_new = file.new_path
                    file_path_old = file.old_path
                    func_name.append(
                        {
                            'file_path_new': file_path_new,
                            'file_path_old': file_path_old,
                            'method_name': method_name
                        }
                    )
                    # if method_name not in func_name:
                    #     func_name.append(file.new_path+'@@'+method_name)
            # self.modified_func_name = func[0]
        except Exception as e:
            ic(e, self.hash)
        return func_name 
    
    def get_func_code(self):
        commit = self.commit
        modified_codes = {}
        try:
            for file in commit.modified_files:
                if str(file.change_type) != 'ModificationType.MODIFY':
                    continue
                for method in file.changed_methods:
                    func_code_after, func_code_before = self.__get_func_code_of_two_versions(method, file)
                    if func_code_after and func_code_before:
                        modified_codes[method.name] = {
                            'before': func_code_before,
                            'after': func_code_after,
                            'file_before': file.old_path,
                            'file_after': file.new_path
                        }
        except Exception as e:
            ic(e)
        return modified_codes

    def get_stmt(self):
        pass
        
    def __get_func_code_of_two_versions(self, method, file):
        method_before = list(filter(lambda x: x.name==method.name, file.methods_before))
        if not method_before:
            return '', ''
        method_before = method_before[0] # choose the first modified method

        src_code = file.source_code
        src_code_before = file.source_code_before

        func_code = self.__get_func_code_from_src(src_code, method)
        func_code_before = self.__get_func_code_from_src(src_code_before, method_before)

        return func_code, func_code_before

    def __get_func_code_from_src(self, source_code, method):
        source_code = source_code.split('\n')
        func_code = '\n'.join(source_code[method.start_line - 1:method.end_line])
        return func_code

    def get_diff_code(self):
        diff_code = []
        commit = self.repo.get_commit(self.hash)
        for mod_files in commit.modified_files:
            diff_code.append(mod_files.diff)
        return diff_code


def test_analyzer():
    pass

if __name__=="__main__":
    test_analyzer()
