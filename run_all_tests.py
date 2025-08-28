#!/usr/bin/env python3
"""
Script pour lancer tous les tests et générer un rapport récapitulatif
"""

import subprocess
import os
import re
from datetime import datetime

def run_django_test(module_name):
    """Lance un test Django et retourne les résultats"""
    print(f"🧪 Test Django: {module_name}")
    
    try:
        os.chdir('/Users/Simplon/Cours/projet_fil_rouge/projet/book_sync')
        result = subprocess.run(
            ['python', 'manage.py', 'test', module_name, '--verbosity=2'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Parse les résultats
        output = result.stdout + result.stderr
        
        # Extraire le nombre de tests
        test_match = re.search(r'Ran (\d+) tests', output)
        total_tests = int(test_match.group(1)) if test_match else 0
        
        # Vérifier si des erreurs
        errors_match = re.search(r'FAILED \(errors=(\d+)\)', output)
        failures_match = re.search(r'FAILED \(failures=(\d+)\)', output)
        both_match = re.search(r'FAILED \(failures=(\d+), errors=(\d+)\)', output)
        
        errors = 0
        failures = 0
        
        if both_match:
            failures = int(both_match.group(1))
            errors = int(both_match.group(2))
        elif errors_match:
            errors = int(errors_match.group(1))
        elif failures_match:
            failures = int(failures_match.group(1))
        
        success = result.returncode == 0
        passed_tests = total_tests - errors - failures
        
        return {
            'module': module_name,
            'success': success,
            'total': total_tests,
            'passed': passed_tests,
            'failed': failures,
            'errors': errors,
            'output': output
        }
        
    except subprocess.TimeoutExpired:
        return {
            'module': module_name,
            'success': False,
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': 1,
            'output': 'TIMEOUT: Test dépassé 120s'
        }
    except Exception as e:
        return {
            'module': module_name,
            'success': False,
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': 1,
            'output': f'ERREUR: {str(e)}'
        }

def run_fastapi_test():
    """Lance les tests FastAPI et retourne les résultats"""
    print(f"🧪 Test FastAPI")
    
    try:
        os.chdir('/Users/Simplon/Cours/projet_fil_rouge/projet/api_IA')
        
        # Installer les dépendances
        subprocess.run(['pip', 'install', '-r', 'requirements_test.txt'], 
                      capture_output=True, check=True)
        
        result = subprocess.run(
            ['pytest', 'test_predict.py', '-v'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        output = result.stdout + result.stderr
        
        # Parse les résultats pytest
        passed_match = re.search(r'(\d+) passed', output)
        failed_match = re.search(r'(\d+) failed', output)
        error_match = re.search(r'(\d+) error', output)
        
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        errors = int(error_match.group(1)) if error_match else 0
        
        total = passed + failed + errors
        success = result.returncode == 0
        
        return {
            'module': 'FastAPI',
            'success': success,
            'total': total,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'output': output
        }
        
    except subprocess.TimeoutExpired:
        return {
            'module': 'FastAPI',
            'success': False,
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': 1,
            'output': 'TIMEOUT: Test dépassé 120s'
        }
    except Exception as e:
        return {
            'module': 'FastAPI',
            'success': False,
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': 1,
            'output': f'ERREUR: {str(e)}'
        }

def generate_report(results):
    """Génère un rapport HTML avec les résultats"""
    
    html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport des Tests - BookSync</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        .header h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #3498db;
        }}
        
        .summary-card.success {{
            border-left-color: #27ae60;
        }}
        
        .summary-card.danger {{
            border-left-color: #e74c3c;
        }}
        
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
        }}
        
        .summary-card .number {{
            font-size: 2em;
            font-weight: bold;
            color: #34495e;
        }}
        
        .modules-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .module-card {{
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            transition: box-shadow 0.3s;
        }}
        
        .module-card:hover {{
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        .module-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .module-name {{
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .status-badge {{
            padding: 5px 15px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            font-size: 0.8em;
        }}
        
        .status-success {{
            background-color: #27ae60;
        }}
        
        .status-failed {{
            background-color: #e74c3c;
        }}
        
        .stats {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 1.5em;
            font-weight: bold;
        }}
        
        .stat-label {{
            font-size: 0.8em;
            color: #7f8c8d;
            text-transform: uppercase;
        }}
        
        .passed {{ color: #27ae60; }}
        .failed {{ color: #e74c3c; }}
        .total {{ color: #3498db; }}
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background-color: #ecf0f1;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background-color: #27ae60;
            transition: width 0.3s;
        }}
        
        .details {{
            margin-top: 40px;
        }}
        
        .details-content {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        
        .timestamp {{
            color: #7f8c8d;
            text-align: center;
            margin-top: 20px;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Rapport des Tests - BookSync</h1>
            <p>Résultats de l'exécution des tests unitaires</p>
        </div>
        
        <div class="summary">
"""

    # Calculer les statistiques globales
    total_modules = len(results)
    successful_modules = sum(1 for r in results if r['success'])
    total_tests = sum(r['total'] for r in results)
    total_passed = sum(r['passed'] for r in results)
    total_failed = sum(r['failed'] + r['errors'] for r in results)
    
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    # Cartes de résumé
    html_content += f"""
            <div class="summary-card success">
                <h3>Modules Réussis</h3>
                <div class="number">{successful_modules}/{total_modules}</div>
            </div>
            
            <div class="summary-card">
                <h3>Tests Totaux</h3>
                <div class="number">{total_tests}</div>
            </div>
            
            <div class="summary-card success">
                <h3>Tests Réussis</h3>
                <div class="number">{total_passed}</div>
            </div>
            
            <div class="summary-card danger">
                <h3>Tests Échoués</h3>
                <div class="number">{total_failed}</div>
            </div>
        </div>
        
        <div class="modules-grid">
"""

    # Cartes pour chaque module
    for result in results:
        success_rate_module = (result['passed'] / result['total'] * 100) if result['total'] > 0 else 0
        
        status_class = "status-success" if result['success'] else "status-failed"
        status_text = "✅ RÉUSSI" if result['success'] else "❌ ÉCHOUÉ"
        
        html_content += f"""
            <div class="module-card">
                <div class="module-header">
                    <div class="module-name">{result['module']}</div>
                    <div class="status-badge {status_class}">{status_text}</div>
                </div>
                
                <div class="stats">
                    <div class="stat">
                        <div class="stat-number total">{result['total']}</div>
                        <div class="stat-label">Total</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number passed">{result['passed']}</div>
                        <div class="stat-label">Réussis</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number failed">{result['failed'] + result['errors']}</div>
                        <div class="stat-label">Échoués</div>
                    </div>
                </div>
                
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {success_rate_module}%"></div>
                </div>
                
                <div style="text-align: center; margin-top: 10px;">
                    <strong>{success_rate_module:.1f}% de réussite</strong>
                </div>
            </div>
"""

    html_content += f"""
        </div>
        
        <div class="details">
            <h2>🎯 Résumé Global</h2>
            <div class="details-content">
                <p><strong>Taux de réussite global :</strong> {success_rate:.1f}%</p>
                <p><strong>Modules testés :</strong> Django (app, accounts, collection, lecture, prediction) + FastAPI</p>
                <p><strong>Couverture :</strong> Modèles, Vues, Authentification, Autorisation, API</p>
            </div>
        </div>
        
        <div class="timestamp">
            📅 Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""

    # Sauvegarder le rapport
    with open('/Users/Simplon/Cours/projet_fil_rouge/projet/rapport_tests.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Générer aussi un fichier texte simple
    txt_content = f"""
🧪 RAPPORT DES TESTS - BOOKSYNC
===============================

📅 Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}

📊 RÉSUMÉ GLOBAL
================
• Modules testés : {total_modules}
• Modules réussis : {successful_modules}
• Tests totaux : {total_tests}
• Tests réussis : {total_passed}
• Tests échoués : {total_failed}
• Taux de réussite : {success_rate:.1f}%

📋 DÉTAIL PAR MODULE
===================
"""
    
    for result in results:
        success_rate_module = (result['passed'] / result['total'] * 100) if result['total'] > 0 else 0
        status_icon = "✅" if result['success'] else "❌"
        
        txt_content += f"""
{status_icon} {result['module'].upper()}
   Total: {result['total']} | Réussis: {result['passed']} | Échoués: {result['failed'] + result['errors']}
   Taux de réussite: {success_rate_module:.1f}%
"""

    with open('/Users/Simplon/Cours/projet_fil_rouge/projet/rapport_tests.txt', 'w', encoding='utf-8') as f:
        f.write(txt_content)

def main():
    print("🚀 Lancement de tous les tests BookSync...")
    print("=" * 50)
    
    # Modules Django à tester
    django_modules = ['app', 'accounts', 'collection', 'lecture', 'prediction']
    
    results = []
    
    # Lancer les tests Django
    for module in django_modules:
        result = run_django_test(module)
        results.append(result)
        
        # Affichage immédiat
        if result['success']:
            print(f"✅ {module}: {result['passed']}/{result['total']} tests réussis")
        else:
            print(f"❌ {module}: {result['passed']}/{result['total']} tests réussis ({result['failed'] + result['errors']} échecs)")
        print("-" * 30)
    
    # Lancer les tests FastAPI
    fastapi_result = run_fastapi_test()
    results.append(fastapi_result)
    
    if fastapi_result['success']:
        print(f"✅ FastAPI: {fastapi_result['passed']}/{fastapi_result['total']} tests réussis")
    else:
        print(f"❌ FastAPI: {fastapi_result['passed']}/{fastapi_result['total']} tests réussis ({fastapi_result['failed'] + fastapi_result['errors']} échecs)")
    
    print("=" * 50)
    print("📊 Génération du rapport...")
    
    # Générer les rapports
    generate_report(results)
    
    print("✅ Rapport HTML généré: rapport_tests.html")
    print("✅ Rapport TXT généré: rapport_tests.txt")
    print("🎉 Tests terminés!")

if __name__ == "__main__":
    main()