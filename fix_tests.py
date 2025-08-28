#!/usr/bin/env python3
"""
Script pour corriger les URLs dans les tests en remplaçant les namespaces par les URLs directes
"""

import os
import re

def fix_accounts_tests():
    """Corriger les URLs dans les tests accounts"""
    file_path = "/Users/Simplon/Cours/projet_fil_rouge/projet/book_sync/accounts/tests.py"
    
    # Dictionnaire des remplacements pour accounts
    replacements = {
        "reverse('accounts:login')": "'/accounts/login/'",
        "reverse('accounts:register')": "'/accounts/register/'",
        "reverse('accounts:logout')": "'/accounts/logout/'",
        "reverse('accounts:profile')": "'/accounts/profile/'",
        "reverse('accounts:subscribe')": "'/accounts/subscribe/'",
        "reverse('accounts:change_password')": "'/accounts/changer-mdp/'",
        "reverse('accounts:update_age_info')": "'/accounts/update-age-info/'",
        "reverse('accounts:update_mature_content')": "'/accounts/update-mature-content/'",
        "reverse('accounts:cancel_subscription')": "'/accounts/cancel-subscription/'",
        "reverse('accounts:delete_user', args=[": "f'/accounts/delete_user/{",
        "reverse('accounts:delete_user', args=[99999])": "'/accounts/delete_user/99999/'",
        "])": "}/'",
        "reverse('index')": "'/home/'",
    }
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    for old, new in replacements.items():
        if "args=[" in old and "99999" not in old:
            # Cas spécial pour delete_user avec argument dynamique
            pattern = r"reverse\('accounts:delete_user', args=\[(.*?)\]\)"
            content = re.sub(pattern, r"f'/accounts/delete_user/{\1}/'", content)
        else:
            content = content.replace(old, new)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Comptes tests corrigés")

def fix_collection_tests():
    """Corriger les URLs dans les tests collection"""
    file_path = "/Users/Simplon/Cours/projet_fil_rouge/projet/book_sync/collection/tests.py"
    
    replacements = {
        "reverse('collection:collection')": "'/collection/collection/'",
        "reverse('collection:search')": "'/collection/search/'",
        "reverse('collection:serie_detail', args=[": "f'/collection/serie/{",
        "])": "}/'",
    }
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    for old, new in replacements.items():
        if "args=[" in old:
            pattern = r"reverse\('collection:serie_detail', args=\[(.*?)\]\)"
            content = re.sub(pattern, r"f'/collection/serie/{\1}/'", content)
        else:
            content = content.replace(old, new)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Collection tests corrigés")

def fix_lecture_tests():
    """Corriger les URLs dans les tests lecture"""
    file_path = "/Users/Simplon/Cours/projet_fil_rouge/projet/book_sync/lecture/tests.py"
    
    replacements = {
        "reverse('lecture:lecture')": "'/ma-lecture/lecture/'",
        "reverse('lecture:add_read', args=[": "f'/ma-lecture/add-read/{",
        "reverse('lecture:remove_read', args=[": "f'/ma-lecture/remove-read/{",
        "])": "}/'",
    }
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    for old, new in replacements.items():
        if "args=[" in old:
            if "add_read" in old:
                pattern = r"reverse\('lecture:add_read', args=\[(.*?)\]\)"
                content = re.sub(pattern, r"f'/ma-lecture/add-read/{\1}/'", content)
            elif "remove_read" in old:
                pattern = r"reverse\('lecture:remove_read', args=\[(.*?)\]\)"
                content = re.sub(pattern, r"f'/ma-lecture/remove-read/{\1}/'", content)
        else:
            content = content.replace(old, new)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Lecture tests corrigés")

def fix_prediction_tests():
    """Corriger les URLs dans les tests prediction"""
    file_path = "/Users/Simplon/Cours/projet_fil_rouge/projet/book_sync/prediction/tests.py"
    
    replacements = {
        "reverse('prediction:prediction_view')": "'/prediction/prediction-view/'",
        "reverse('prediction:category_preference_view')": "'/prediction/category-preference-view/'", 
        "reverse('prediction:save_age')": "'/prediction/save-age/'",
    }
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Prediction tests corrigés")

if __name__ == "__main__":
    print("🔧 Correction des tests...")
    fix_accounts_tests()
    fix_collection_tests() 
    fix_lecture_tests()
    fix_prediction_tests()
    print("✅ Tous les tests ont été corrigés!")