from analysis.patch_analyzer import PatchAnalyzer
import config.config as config
import os
import json
import logging
import utils.get_path_new as get_path
import copy
import shutil
import re
from subprocess import Popen, PIPE

logger = logging.getLogger(__name__)

class CriterionExtractor:
    """A class to extract and save criterions from a patch."""

    def __init__(self):
        # commit_id = commit_id
        # self.patch_analyzer = PatchAnalyzer(url, commit_id)
        pass

    def get_criteroin_from_patch(self, url, commit_id):
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
                - modification: str
        """
        patch_analyzer = PatchAnalyzer(url, commit_id)
        info = patch_analyzer.get_commit_info()
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
                        modifcation = 'DELETE'
                        criterions.append({
                            'criterion': del_stmt_info,  # line, code
                            'commit_id': commit_id,
                            'version': version,  # old, new
                            'file_path': file_path,  # old, new
                            'func_name': func_name,
                            'func_line': func_line,  # start, end
                            'func_code': func_code,  # old, new
                            'file_code': file_code,  # old, new
                            'modification': modifcation
                        })
                    func_added_stmt = func_stmt['added']
                    for add_stmt_info in func_added_stmt:
                        modifcation = 'ADD'
                        criterions.append({
                            'criterion': add_stmt_info,  # line, code
                            'commit_id': commit_id,
                            'version': version,  # old, new
                            'file_path': file_path,  # old, new
                            'func_name': func_name,
                            'func_line': func_line,  # start, end
                            'func_code': func_code,  # old, new
                            'file_code': file_code,  # old, new
                            'modification': modifcation
                        })
        return criterions
    
    def get_criterion_from_response(self, parsed_response, commit_id):
        criterions = []
        further_stmts = parsed_response.get("further_slicing", {})
        for stmt in further_stmts:
            stmt_code_extract = stmt.get("statement")
            stmt_info = stmt.get("statement_info")
            
            # get filepath, function name, line from statement_info
            stmt_info_parts = stmt_info.split(" | ")
            if len(stmt_info_parts) != 3:
                logger.warning(f"Invalid statement_info: {stmt_info}")
                continue
            filepath_extract, funcname_extract, line_extract = stmt_info_parts
            line_num = int(re.search(r'\d+', line_extract).group())

            # get direction, graph        
            direction = self._get_response_direction(stmt['slicing_direction'])
            graph = self._get_response_graph_type(stmt['code_representation_graph'])

            # get modification and filepath
            modification = ""
            if config.OLD_CODE_DIRNAME in filepath_extract:
                modification = "DELETE"
                filepath = filepath_extract.split(config.OLD_CODE_DIRNAME+"/")[-1]
            elif config.NEW_CODE_DIRNAME in filepath_extract:
                modification = "ADD"
                filepath = filepath_extract.split(config.NEW_CODE_DIRNAME+"/")[-1]
            else:
                logger.error(f"Cannot determine modification: {filepath_extract}")

            # get func_name
            funcname_clean = funcname_extract.split('(')[0].split()[-1]

            # init criterion
            criterion = {
                "criterion": {
                    "line": line_num,
                    "code": stmt_code_extract
                },
                "commit_id": commit_id,
                "file_path": {
                    "old": filepath,
                    "new": filepath,
                },
                "func_name": funcname_clean,
                "func_line": {},
                "modification": modification,
                "direction": direction,
                "graph": graph,
            }

            # absoulte path of the code file
            save_root = get_path.get_save_rootpath(commit_id=commit_id)
            src_relpath = get_path.get_src_relpath(modification=modification, file_path_dict=criterion['file_path'])
            code_basename = os.path.basename(src_relpath)
            
            # code file
            code_root = get_path.get_code_rootpath(save_root=save_root)
            code_filepath = get_path.get_code_savepath(code_root=code_root, src_relpath=src_relpath)

            # module dir
            module_dirpath = os.path.dirname(code_filepath)

            # meta file
            meta_root = get_path.get_meta_rootpath(save_root=save_root)
            meta_filepath = get_path.get_mata_savepath(meta_root=meta_root, src_relpath=src_relpath, code_basename=code_basename, funcname=funcname_clean, linenum=line_num, modification=modification)

            criterion['save_root'] = save_root
            criterion['save_file_code_filepath'] = code_filepath
            criterion['save_module_dirpath'] = module_dirpath
            criterion['save_meta_filepath'] = meta_filepath

            # check if the extracted funcname is correct
            funcname, func_start, func_end = self._get_funcname_from_line(file_path=code_filepath, line_num=line_num)        
            if not funcname_clean == funcname:
                logger.error(f"Function name mismatch: {funcname_extract} != {funcname}")
                continue
            criterion['func_line'] = {
                "start": func_start,
                "end": func_end
            }

            # check if the extracted code is correct
            stmt_code = self._get_code_from_line(file_path=code_filepath, line_num=line_num)
            if stmt_code not in stmt_code_extract:
                logger.error(f"Statement code mismatch: {stmt_code} not in {stmt_code_extract}")
                continue

            # save criterion
            with open(meta_filepath, 'w') as f:
                json.dump([criterion], f, indent=2)
            logger.info(f"Extracted criterion from response, save to: {meta_filepath}")
            
            criterions.append(criterion)
            logger.info(f"Extracted criterion (Checked): {stmt_info}")
        
        return criterions
    

    def _get_response_graph_type(self, response_graph_type):
        if response_graph_type == "Control Flow Graph":
            graph_type = "cfg"
        elif response_graph_type == "Program Dependence Graph":
            graph_type = "pdg"
        elif response_graph_type == "Data Dependency Graph":
            graph_type = "ddg"
        elif response_graph_type == "Control Dependency Graph":
            graph_type = "cdg"
        elif response_graph_type == "Abstract Syntax Tree":
            graph_type = "ast"
        elif response_graph_type == "Code Property Graph":
            graph_type = "cpg"
        elif response_graph_type == "Call Graph":
            graph_type = "cg"
        else:
            logger.error(f"Invalid graph type: {response_graph_type}")
            graph_type = "all"
        
        return graph_type
    

    def _get_response_direction(self, response_direction):
        if response_direction not in ['forward', 'backward', 'bidirectional']:
            logger.error(f"Invalid slicing direction: {response_direction}")
            response_direction = "bidirectional"
        
        return response_direction
    

    def _execute_command(self, command, cwd):
        try:
            p = Popen(command,stdout=PIPE,stderr=PIPE,cwd=cwd,shell=True)
            content, _ = p.communicate()
            out = content.decode("utf8","ignore")
            return out
        except Exception as e:
            logger.error(f"[Command execution failed] Execution error: {e.stderr}")
            return ''


    def _get_code_from_line(self, file_path, line_num):
        with open(file_path, "r", errors="ignore") as rfile:
            lines = rfile.readlines()
            return lines[line_num - 1].strip()
    

    def _get_funcname_from_line(self, file_path, line_num):
        cmd2 = 'ctags --fields=+ne-t -o - --sort=no --excmd=number %s' % file_path
        res = self._execute_command(cmd2, ".")
        if not res:
            with open(file_path, "r", errors="ignore") as rfile:
                file_str = rfile.read()
            if not file_str:
                return None
            else:
                logger.error(f"Empty Ctags Result [{file_path}]")
                return None
                
        lines = res.splitlines()

        for line in lines:
            fields = line.split()
            if 'f' in fields:            
                start_num = self._get_num(fields, 'line:')
                end_num = self._get_num(fields, 'end:')

                with open(file_path, "r", errors="ignore") as rfile:
                    lines = rfile.readlines()
                func_code = lines[start_num - 1:end_num]

                if start_num is None or end_num is None:
                    continue
                if line_num >= start_num and line_num <= end_num:
                    func_first_line = func_code[0]
                    funcname = func_first_line.strip().split('(')[0].split()[-1]
                    return funcname, start_num, end_num
        
        return None, None, None
    

    def _get_num(self, fields, tag):
        for item in fields:
            if tag in item:
                tag_list = item.split(":")
                return int(tag_list[-1])


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
                - modification: str
        """
        for criterion in criterions:
            line_num = criterion['criterion']['line']
            commit_id = criterion['commit_id']
            func_name = criterion['func_name']
            modification = criterion['modification']
            
            save_root = get_path.get_save_rootpath(commit_id=commit_id)
            src_relpath = get_path.get_src_relpath(modification=modification, file_path_dict=criterion['file_path'])
            code_basename = os.path.basename(src_relpath)
            
            # code file
            code_root = get_path.get_code_rootpath(save_root=save_root)
            code_filepath = get_path.get_code_savepath(code_root=code_root, src_relpath=src_relpath)

            # module dir
            module_dirpath = os.path.dirname(code_filepath)

            # meta file
            meta_root = get_path.get_meta_rootpath(save_root=save_root)
            meta_filepath = get_path.get_mata_savepath(meta_root=meta_root, src_relpath=src_relpath, code_basename=code_basename, funcname=func_name, linenum=line_num, modification=modification)

            criterion['save_root'] = save_root
            criterion['save_file_code_filepath'] = code_filepath
            criterion['save_module_dirpath'] = module_dirpath
            criterion['save_meta_filepath'] = meta_filepath

            if modification=='DELETE':
                repo_version = criterion['version']['old']
                repo_file_path = criterion['file_path']['old']
                repo_module_dirpath = self._get_module_path(repo_file_path)
                repo_filecode = criterion['file_code']['old']
            elif modification=='ADD':
                repo_version = criterion['version']['new']
                repo_file_path = criterion['file_path']['new']
                repo_module_dirpath = self._get_module_path(repo_file_path)
                repo_filecode = criterion['file_code']['new']

            if save_module:
                self._save_module(repo_version=repo_version, repo_module_path=repo_module_dirpath, module_dirpath=module_dirpath, overwrite=config.MODULE_OVERWRITE)

            if save_file:
                self._save_file(file_content=repo_filecode, file_path=code_filepath, overwrite=config.CODE_FILE_OVERWRITE)
            
            if save_meta:
                self._save_criterion_meta([criterion], meta_filepath)

        return criterions

    
    def _save_module(self, repo_version, repo_module_path, module_dirpath, overwrite=False):
        """copy local_module_path to module_dirpath, default to overwrite."""
        # checkout the version
        if not os.path.exists(repo_module_path):
            logger.error(f"[Save module failed] Cannot find repo_module_path: {repo_module_path}")
            return
        os.system(f"git -C {config.LINUX} checkout {repo_version} -- {repo_module_path}")
        logger.info(f"Checked out {repo_version} to {repo_module_path}")
        logger.debug(f"cmd: git -C {config.LINUX} checkout {repo_version} -- {repo_module_path}")

        if os.path.exists(module_dirpath):
            if overwrite:
                if os.listdir(module_dirpath):
                    logger.warning(f"[Remove module directory] Module directory exists (not empty): {module_dirpath}")
                shutil.rmtree(module_dirpath)
            else:
                logger.info(f"Module directory already exists and overwrite is not enabled: {module_dirpath}")
                return

        shutil.copytree(repo_module_path, module_dirpath)
        logger.info(f"Copied {repo_module_path} to {module_dirpath}")
        

    def _get_module_path(self, repo_file_path, root=config.LINUX):
        module_dir = os.path.dirname(repo_file_path)
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
        criterions = copy.deepcopy(criterions)
        for criterion in criterions:
            del criterion['file_code']
            del criterion['func_code']
            meta.append(criterion)
            
        with open(meta_filepath, 'w') as f:
            f.write(json.dumps(meta, indent=2))

        logger.info(f"Meta file saved to {meta_filepath}")

    
    def _save_file(self, file_content, file_path, overwrite=False):
        if os.path.exists(file_path):
            if overwrite:
                logger.warning(f"Overwrite file: {file_path}")
            else:
                logger.info(f"file already exists and not overwrite: {file_path}")
                return
        else:
            logger.error(f"[File save failed] Cannot find file: {file_path}")

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        with open(file_path, 'w') as f:
            f.write(file_content)

        logger.info(f"File saved to {file_path}")

def test():
    url = config.LINUX
    hash_id = "97bf6f81b29a8efaf5d0983251a7450e5794370d"
    extractor = CriterionExtractor(url, hash_id)
    criterions = extractor.get_criteroin_from_patch()
    extractor.save_criterion(criterions)

if __name__ == "__main__":
    test()