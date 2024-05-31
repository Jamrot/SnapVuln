from patch_analyzer import PatchAnalyzer
import config 
import os
import json
import logging

logger = logging.getLogger(__name__)

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

    def save_criterion(self, criterions, save_file=True, save_meta=True, save_module=True):
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
            func_name = criterion['func_name']
            file_path_old = criterion['file_path']['old']
            file_path_new = criterion['file_path']['new']

            commit_id_short = commit_id[:8]
            # funcname_line = "-".join([func_name, str(criterion_line)])
            save_root = os.path.join(config.CODE_ROOT, commit_id_short)
            save_filename_base = "-".join([commit_id_short, func_name, str(criterion_line)])
            criterion['save_root'] = save_root
            criterion['save_filename_base'] = save_filename_base

            if save_file:
                # save code (old version) to code_filepath 
                code_filename = "-".join([config.CODE_FILENAME_START, save_filename_base])+'.c'
                code_filepath = os.path.join(save_root, save_filename_base, code_filename)
                self._save_file(file_code_old, code_filepath, confirm=config.CODE_FILE_CONFIRM)

                criterion['save_file_code_old_filepath'] = code_filepath

            if save_module:
                # save old module to module_dir
                module_dir = os.path.dirname(file_path_old)
                module_dirname = "-".join([config.MODULE_DIRNAME_START, commit_id_short, "_".join(module_dir.split("/"))])
                module_dirpath = os.path.join(save_root, module_dirname)
                self._save_module(criterion=criterion, module_dirpath=module_dirpath, confirm=config.MODULE_CONFIRM, overwrite=config.MODULE_OVERWRITE)

                criterion['save_module_dirpath'] = module_dirpath
            
            if save_meta:
                # save criterion meta information to meta_filepath
                meta_filename = "-".join([config.META_FILENAME_START, save_filename_base])+'.json'
                meta_filepath = os.path.join(save_root, save_filename_base, meta_filename)
                self._save_criterion_meta([criterion], meta_filepath)

    
    def _save_module(self, criterion, module_dirpath, confirm=True, overwrite=True):
        """copy local_module_path to module_dirpath, default to overwrite."""
        file_path_new = criterion['file_path']['new']
        old_version = criterion['version']['old']
        local_module_path = self._get_module_path(file_path_new)
        if not os.path.exists(local_module_path):
            logger.error(f"Local module path {local_module_path} does not exist")
            exit() 
        
        # checkout the version
        os.system(f"git -C {config.LINUX} checkout {old_version} -- {file_path_new}")

        if os.path.exists(module_dirpath):
            if not len(os.listdir(module_dirpath)) == 0:
                logger.warning(f"Module directory {module_dirpath} already exists and is not empty")
                
                if confirm:
                    confirm_input = input(f"{module_dirpath} already exists, overwrite (y/n)")              
                    if confirm_input.lower() != 'y':
                        overwrite = False
                if overwrite:
                    logger.warning(f"Overwriting module directory {module_dirpath}")
                    os.system(f"rm -rf {module_dirpath}")

        os.system(f"cp -r {local_module_path} {module_dirpath}")
        

    def _get_module_path(self, file_path, root=config.LINUX):
        module_dir = os.path.dirname(file_path)
        module_path = os.path.join(root, module_dir)
        return module_path

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
            del criterion['file_code']
            del criterion['func_code']
            meta.append(criterion)
            # meta.append({
            #     'criterion': criterion['criterion'],
            #     'commit_id': criterion['commit_id'],
            #     'version': criterion['version'],
            #     'file_path': criterion['file_path'],
            #     'func_name': criterion['func_name'],
            #     'func_line': criterion['func_line'],
            # })
            
        with open(meta_filepath, 'w') as f:
            f.write(json.dumps(meta, indent=4))

        logger.info(f"Meta file saved to {meta_filepath}")

    def _save_file(self, file_content, file_path, confirm=True):
        """Saves content to a file, default to overwrite.

        Parameters:
            file_content (str): The content to be saved in the file.
            file_path (str): The path where the file will be saved.
            confirm (bool): Whether to ask for confirmation before overwriting the file.
        """
        if os.path.exists(file_path):
            logger.warning(f"File {file_path} already exists")
            confirm_input = input(f"File {file_path} already exists, overwrite? (y/n)") if confirm else 'y' # default to overwrite
            if confirm_input.lower() != 'y':
                return
            else:
                logger.warning(f"Overwriting file {file_path}")

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        with open(file_path, 'w') as f:
            f.write(file_content)

        logger.info(f"Code file saved to {file_path}")

def test():
    url = config.LINUX
    hash_id = "97bf6f81b29a8efaf5d0983251a7450e5794370d"
    extractor = CriterionExtractor(url, hash_id)
    criterions = extractor.get_criterion_from_patch()
    extractor.save_criterion(criterions)

if __name__ == "__main__":
    test()