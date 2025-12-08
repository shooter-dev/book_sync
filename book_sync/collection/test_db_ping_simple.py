import pytest
import os
import time

def test_database_ping():
    """Test simple de ping de la base de données Azure"""

    # Configure les settings Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_sync.settings')

    try:
        import django
        django.setup()

        from django.db import connection

        # Test de connexion simple avec timer
        start_time = time.time()

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 as ping_result")
            result = cursor.fetchone()

        end_time = time.time()

        # Vérifications
        assert result[0] == 1, "La base de données n'a pas retourné le résultat attendu"

        response_time = (end_time - start_time) * 1000  # Convertir en ms
        print(f"Database ping successful! Response time: {response_time:.2f}ms")

        # Le ping devrait être raisonnablement rapide (moins de 5 secondes)
        assert response_time < 5000, f"Response time too slow: {response_time:.2f}ms"

        print("✅ Database connection is working properly!")
        
        print("✅ the pytest worked!")

    except ImportError as e:
        pytest.skip(f"Django not available: {e}")
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")