from patch_analyzer import PatchAnalyzer

def extract_patch_info(url, hash, desc_tags_prefixes):
    analyzer = PatchAnalyzer(url, hash)
    author, date = analyzer.get_author_and_date()
    full_desc, clean_desc = analyzer.get_description(desc_tags_prefixes)
    modified_funcs = analyzer.get_modified_func_in_commit()
    modified_files = analyzer.get_modified_files()
    modified_codes = analyzer.get_modified_func_code()
    diff_code = analyzer.get_diff_code()
    return author, date, full_desc, clean_desc, modified_funcs, modified_codes, modified_files, diff_code

def get_criterion_from_patch(analyzer):
    diff_code = analyzer.get_diff_code()
    print(diff_code)

if __name__ == "__main__":
    url = ""