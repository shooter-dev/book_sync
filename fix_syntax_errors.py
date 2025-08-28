#!/usr/bin/env python3
"""
Script pour corriger les erreurs de syntaxe dans les tests
"""

import re

def fix_file(file_path, fixes):
    with open(file_path, 'r') as f:
        content = f.read()
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    with open(file_path, 'w') as f:
        f.write(content)

# Corrections pour lecture/tests.py
lecture_fixes = [
    (r"self\.volumes\[(\d+)\}\]/", r"self.volumes[\1]]"),
    (r"response\.context\['(\w+)'\}\]/", r"response.context['\1'])"),
    (r"stats\['(\w+)'\}\]/", r"stats['\1'])"),
    (r"self\.volumes_serie1\[(\d+)\}\]/", r"self.volumes_serie1[\1]]"),
    (r"self\.volumes_serie2\[(\d+)\}\]/", r"self.volumes_serie2[\1]]"),
]

# Corrections pour accounts/tests.py  
accounts_fixes = [
    (r"response\.context\['(\w+)'\}\]/", r"response.context['\1'])"),
]

# Corrections pour collection/tests.py
collection_fixes = [
    (r"series_with_volumes\[self\.serie\}\]/", r"series_with_volumes[self.serie])"),
    (r"response\.context\['(\w+)'\}\]/", r"response.context['\1'])"),
]

if __name__ == "__main__":
    print("🔧 Correction des erreurs de syntaxe...")
    
    fix_file("/Users/Simplon/Cours/projet_fil_rouge/projet/book_sync/lecture/tests.py", lecture_fixes)
    print("✅ lecture/tests.py corrigé")
    
    fix_file("/Users/Simplon/Cours/projet_fil_rouge/projet/book_sync/accounts/tests.py", accounts_fixes)
    print("✅ accounts/tests.py corrigé")
    
    fix_file("/Users/Simplon/Cours/projet_fil_rouge/projet/book_sync/collection/tests.py", collection_fixes)
    print("✅ collection/tests.py corrigé")
    
    print("✅ Toutes les erreurs de syntaxe ont été corrigées!")