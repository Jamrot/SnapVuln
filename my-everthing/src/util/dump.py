import config
from pydriller import Git
from icecream import ic


class PatchAnalyzer:
    def __init__(self, url, commit_id):
        self.url = url
        self.commit_id = commit_id
        self.repo = Git(self.url)
        self.commit = self.repo.get_commit(self.commit_id)

    def get_author_and_date(self):
        commit = self.commit
        return commit.author, commit.author_date

    def get_description(self, desc_tags_prefixes):
        commit = self.commit
        lines = commit.msg.splitlines()
        lines_filter = list(
            filter(lambda x: not x.startswith(tuple(desc_tags_prefixes)), lines))
        clean_msg = "\n".join(lines_filter)
        return commit.msg, clean_msg

    def get_version(self):
        """get the version before and after the commit"""
        commit = self.commit
        version_before = commit.parents[0].hash
        version_after = commit.hash
        return version_before, version_after
    
    def get_file_path(self):
        commit = self.commit
        file_path = []
        for file in commit.modified_files:
            file_path_new = file.new_path
            file_path_old = file.old_path
            file_path.append({
                'file_path_new': file_path_new,
                'file_path_old': file_path_old
            })
        return file_path

    def get_file_code(self):
        commit = self.commit
        # modified_files = self.get_file_path()
        modified_codes = []
        for file in commit.modified_files:
            src_code = file.source_code
            src_code_before = file.source_code_before
            file_path_new = file.new_path
            file_path_old = file.old_path
        
            modified_codes.append({
                'file_path_new': file_path_new,
                'file_path_old': file_path_old,
                'file_code_new': src_code,
                'file_code_old': src_code_before
            })
        
        return modified_codes


    def get_func_name(self):
        commit = self.commit
        func_name = []
        try:
            for file in commit.modified_files:
                src_code = file.source_code
                src_code_before = file.source_code_before
                file_path_new = file.new_path
                file_path_old = file.old_path
                for method in file.changed_methods:
                    method_name = method.name
                    func_name.append({
                        'file_path_new': file_path_new,
                        'file_path_old': file_path_old,
                        'file_code_new': src_code,
                        'file_code_old': src_code_before,
                        'func_name': method_name,
                    })
        except Exception as e:
            ic(e, self.commit_id)
        return func_name 
    
    def get_func_code(self, method):
        commit = self.commit
        commit_id = self.commit_id
        func_code = []
        for file in commit.modified_files:
            src_code = file.source_code
            src_code_before = file.source_code_before
            file_path_new = file.new_path
            file_path_old = file.old_path
            if str(file.change_type) != 'ModificationType.MODIFY':
                print(str(file.change_type))
                continue
            for method in file.changed_methods:
                method_name = method.name
                func_code_after, func_code_before = self.__get_func_code_of_two_versions(method, file)
                if func_code_after and func_code_before:
                    func_code.append({
                        'file_path_new': file_path_new,
                        'file_path_old': file_path_old,
                        'file_code_new': src_code,
                        'file_code_old': src_code_before,
                        'func_name': method_name,
                        'func_code_new': func_code_after,
                        'func_code_old': func_code_before
                    })
        return func_code

    def get_stmt(self):
        commit = self.commit
        commit_id = self.commit_id
        stmt = []
        try:
            for file in commit.modified_files:
                # for method in file.changed_methods:
                diff_parsed = file.diff_parsed
                file_path_new = file.new_path
                file_path_old = file.old_path
                diff_parsed.update({
                    'file_path_new': file_path_new,
                    'file_path_old': file_path_old
                })
                # print(diff_parsed)
                # for stmt in method.changed_statements:
                stmt.append(diff_parsed)
        except Exception as e:
            ic(e)
        
        return stmt

    def get_diff_code(self):
        diff_code = []
        commit = self.repo.get_commit(self.commit_id)
        for mod_files in commit.modified_files:
            diff_code.append(mod_files.diff_parsed)
        return diff_code
        
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


def test_analyzer():
    url = config.LINUX
    hash_id = "97bf6f81b29a8efaf5d0983251a7450e5794370d"
    patch_analyzer = PatchAnalyzer(url, hash_id)
    info = {}
    stmt = patch_analyzer.get_stmt()
    func_code = patch_analyzer.get_func_code()

    print(info[hash_id])


if __name__=="__main__":
    test_analyzer()
