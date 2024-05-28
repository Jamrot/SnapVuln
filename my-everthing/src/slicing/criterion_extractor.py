from patch_analyzer import PatchAnalyzer
import config 
import os
from icecream import ic
import json

class CriterionExtractor:
    """A class to extract and save criterions from a patch."""

    def __init__(self, url, hash_id):
        """Initializes CriterionExtractor to creates a PatchAnalyzer instance.

        Parameters:
            url (str): The URL of the Git repository.
            hash_id (str): The commit hash ID.
        """
        self.patch_analyzer = PatchAnalyzer(url, hash_id)

    def get_criterion_from_patch(self):
        """Extracts criterions from a patch using the given PatchAnalyzer.

        Returns:
            list: A list of dictionaries containing criterions with the following keys:
                - criterion: {'line': int, 'code': str}
                - commit_id: str
                - version: {'old': str, 'new': str}
                - file_path: {'old': str, 'new': str}
                - func_name: str
                - func_line: {'start': int, 'end': int}
                - func_code: {'old': str, 'new': str}
                - file_code: {'old': str, 'new': str}
        """
        info = self.patch_analyzer.get_commit_info()
        criterions = []
        for commit_id in info:
            commit = info[commit_id]
            version = commit['version']
            for file in commit['files']:
                file_path = file['file_path']
                file_code = file['file_code']
                functions = file['functions']
                for func_info in functions:
                    func_name = func_info['func_name']
                    func_line = func_info['func_line']
                    func_code = func_info['func_code']
                    func_stmt = func_info['func_stmt']
                    func_deleted_stmt = func_stmt['deleted']
                    for del_stmt_info in func_deleted_stmt:
                        criterions.append({
                            'criterion': del_stmt_info,  # line, code
                            'commit_id': commit_id,
                            'version': version,  # old, new
                            'file_path': file_path,  # old, new
                            'func_name': func_name,
                            'func_line': func_line,  # start, end
                            'func_code': func_code,  # old, new
                            'file_code': file_code,  # old, new
                        })
        return criterions

    def save_criterion(self, criterions):
        """Saves the extracted criterions to CODE_ROOT/commit_id directory.

        Parameters:
            criterions (list): A list of dictionaries containing criterion information.
                - criterion: {'line': int, 'code': str}
                - commit_id: str
                - version: {'old': str, 'new': str}
                - file_path: {'old': str, 'new': str}
                - func_name: str
                - func_line: {'start': int, 'end': int}
                - func_code: {'old': str, 'new': str}
                - file_code: {'old': str, 'new': str}
        """
        for criterion in criterions:
            criterion_line = criterion['criterion']['line']
            file_code = criterion['file_code']
            file_code_old = file_code['old']
            file_code_new = file_code['new']
            commit_id = criterion['commit_id']

            commit_id_short = commit_id[:8]
            save_filename = f"file_code_old-{commit_id_short}_{criterion_line}.c"
            save_filepath = os.path.join(config.CODE_ROOT, commit_id_short, save_filename)
            self._save_file(file_code_old, save_filepath)
            meta_filename = f"meta-{commit_id_short}_{criterion_line}.json"
            meta_filepath = os.path.join(config.CODE_ROOT, commit_id_short, meta_filename)
            self._save_criterion_meta([criterion], meta_filepath)

    def _save_criterion_meta(self, criterions, meta_filepath):
        """Saves the meta information of the extracted criterions to a file.

        Parameters:
            criterions (list): A list of dictionaries containing criterion information.
                - criterion: {'line': int, 'code': str}
                - commit_id: str
                - version: {'old': str, 'new': str}
                - file_path: {'old': str, 'new': str}
                - func_name: str
                - func_line: {'start': int, 'end': int}
                - func_code: {'old': str, 'new': str}
                - file_code: {'old': str, 'new': str}
        """
        meta = []
        for criterion in criterions:
            meta.append({
                'criterion': criterion['criterion'],
                'commit_id': criterion['commit_id'],
                'version': criterion['version'],
                'file_path': criterion['file_path'],
                'func_name': criterion['func_name'],
                'func_line': criterion['func_line'],
            })
        with open(meta_filepath, 'w') as f:
            f.write(json.dumps(meta, indent=4))

        ic(f"Meta file saved to {meta_filepath}")

    def _save_file(self, file_content, file_path):
        """Saves content to a file, asking for confirmation if the file already exists.

        Parameters:
            file_content (str): The content to be saved in the file.
            file_path (str): The path where the file will be saved.
        """
        if os.path.exists(file_path):
            ic(f"File {file_path} already exists")
            confirm = input("Do you want to overwrite this file? (y/n)")
            if confirm.lower() != 'y':
                return

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        with open(file_path, 'w') as f:
            f.write(file_content)

        ic(f"Code file saved to {file_path}")

def main():
    url = config.LINUX
    hash_id = "97bf6f81b29a8efaf5d0983251a7450e5794370d"
    extractor = CriterionExtractor(url, hash_id)
    criterions = extractor.get_criterion_from_patch()
    extractor.save_criterion(criterions)

if __name__ == "__main__":
    main()