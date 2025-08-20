import os
import json
import time
from typing import Set
import psycopg2

from mangacollec.author import Author
from mangacollec.client import MangaCollecAPIClient
from mangacollec.job import Job
from mangacollec.kinds.entity.kind import Kind
from mangacollec.series.entity.type import Type
from mangacollec.series.entity.task import Task
from mangacollec.series.entity.serie import Serie
from mangacollec.publishers.entity.publisher import Publisher
from mangacollec.volumes.entity.volume import Volume
from mangacollec.series.endpoint.serie_endpoint import SerieEndpoint
from mangacollec.series.responses.serie_response import SerieEndpointResponse

# Constantes
RESTART_MESSAGE = "🔄 Vous pouvez relancer le script pour reprendre où vous vous êtes arrêté"


def add_jobs_bdd(db_conn, job: Job):
    """
    Ajoute un job/métier à la base de données via une connexion psycopg2.
    Si le job existe déjà, met à jour les données.

    :param db_conn: Connexion psycopg2 à la base de données
    :param job: Objet Job à insérer ou mettre à jour
    """
    cur = db_conn.cursor()

    # UPSERT : INSERT avec ON CONFLICT DO UPDATE
    cur.execute("""
        INSERT INTO collection_jobs (id, title) 
        VALUES (%s, %s)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title
    """, (job.id, job.title))

    db_conn.commit()
    # print(f"✅ Job inséré/mis à jour: {job.title}")


def add_authors_bdd(db_conn, author: Author):
    """
    Ajoute un auteur à la base de données via une connexion psycopg2.
    Si l'auteur existe déjà, met à jour les données.

    :param db_conn: Connexion psycopg2 à la base de données
    :param author: Objet Author à insérer ou mettre à jour
    """
    cur = db_conn.cursor()

    # UPSERT : INSERT avec ON CONFLICT DO UPDATE
    cur.execute("""
        INSERT INTO collection_authors (id, name, first_name) 
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            first_name = EXCLUDED.first_name
    """, (author.id, author.name, author.first_name))

    db_conn.commit()
    # print(f"✅ Auteur inséré/mis à jour: {author.name} {author.first_name}")


def add_kinds_bdd(db_conn, kind: Kind):
    """
    Ajoute une catégorie (kind) à la base de données via une connexion psycopg2.
    Si la catégorie existe déjà, met à jour les données.

    :param db_conn: Connexion psycopg2 à la base de données
    :param kind: Objet Kind à insérer ou mettre à jour
    """
    cur = db_conn.cursor()

    # UPSERT : INSERT avec ON CONFLICT DO UPDATE
    cur.execute("""
        INSERT INTO collection_kind (id, title) 
        VALUES (%s, %s)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title
    """, (kind.id, kind.title))

    db_conn.commit()
    # print(f"✅ Catégorie insérée/mise à jour: {kind.title}")


def add_genres_bdd(db_conn, genre: Type):
    """
    Ajoute un type de série (genre) à la base de données via une connexion psycopg2.
    Si le type existe déjà, met à jour les données.

    :param db_conn: Connexion psycopg2 à la base de données
    :param genre: Objet Type à insérer ou mettre à jour
    """
    cur = db_conn.cursor()

    # UPSERT : INSERT avec ON CONFLICT DO UPDATE
    cur.execute("""
        INSERT INTO collection_genre (id, title, to_display) 
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            to_display = EXCLUDED.to_display
    """, (genre.id, genre.title, genre.to_display))

    db_conn.commit()
    # print(f"✅ Genre inséré/mis à jour: {genre.title}")


def add_tasks_bdd(db_conn, task: Task):
    """
    Ajoute une tâche (relation auteur-série-métier) à la base de données via une connexion psycopg2.
    Si la tâche existe déjà, met à jour les données.

    :param db_conn: Connexion psycopg2 à la base de données
    :param task: Objet Task à insérer ou mettre à jour
    """
    cur = db_conn.cursor()

    # UPSERT : INSERT avec ON CONFLICT DO UPDATE
    cur.execute("""
        INSERT INTO collection_tasks (id, id_author_id, id_jobs_id, id_series_id) 
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            id_author_id = EXCLUDED.id_author_id,
            id_jobs_id = EXCLUDED.id_jobs_id,
            id_series_id = EXCLUDED.id_series_id
    """, (task.id, task.author_id, task.job_id, task.series_id))

    db_conn.commit()
    # print(f"✅ Tâche insérée/mise à jour: {task.id}")


def add_series_bdd(db_conn, serie: Serie, publisher: Publisher):
    """
    Ajoute une série à la base de données via une connexion psycopg2.
    Si la série existe déjà, met à jour les données.

    :param db_conn: Connexion psycopg2 à la base de données
    :param serie: Objet Serie à insérer ou mettre à jour
    :param publisher: Objet Publisher pour l'éditeur de la série
    """
    cur = db_conn.cursor()

    # UPSERT : INSERT avec ON CONFLICT DO UPDATE
    cur.execute("""
        INSERT INTO collection_serie (id, title, adult_content, genre_id, publisher_id) 
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            adult_content = EXCLUDED.adult_content,
            genre_id = EXCLUDED.genre_id,
            publisher_id = EXCLUDED.publisher_id
    """, (serie.id, serie.title, serie.adult_content, serie.type_id, publisher.id))

    db_conn.commit()
    # print(f"✅ Série insérée/mise à jour: {serie.title}")


def add_publishers_bdd(db_conn, publisher: Publisher):
    """
    Ajoute un éditeur à la base de données via une connexion psycopg2.
    Si l'éditeur existe déjà, met à jour les données.

    :param db_conn: Connexion psycopg2 à la base de données
    :param publisher: Objet Publisher à insérer ou mettre à jour
    """
    cur = db_conn.cursor()

    # UPSERT : INSERT avec ON CONFLICT DO UPDATE
    cur.execute("""
        INSERT INTO collection_publisher (id, title) 
        VALUES (%s, %s)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title
    """, (publisher.id, publisher.title))

    db_conn.commit()
    # print(f"✅ Publisher inséré/mis à jour: {publisher.title}")


def add_volumes_bdd(db_conn, volume: Volume, serie_id: str):
    """
    Ajoute un volume à la base de données via une connexion psycopg2.
    Si le volume existe déjà, met à jour les données.

    :param db_conn: Connexion psycopg2 à la base de données
    :param volume: Objet Volume à insérer ou mettre à jour
    :param serie_id: ID de la série à laquelle le volume appartient
    """
    cur = db_conn.cursor()

    # Gérer les valeurs null pour les champs obligatoires
    title = volume.title or f"Volume {volume.number}"
    release_date = volume.release_date or '1900-01-01'  # Date par défaut si None

    # UPSERT : INSERT avec ON CONFLICT DO UPDATE
    cur.execute("""
        INSERT INTO collection_volume (id, title, number, release_date, isbn, possessions_count, image_url, serie_id) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            number = EXCLUDED.number,
            release_date = EXCLUDED.release_date,
            isbn = EXCLUDED.isbn,
            possessions_count = EXCLUDED.possessions_count,
            image_url = EXCLUDED.image_url,
            serie_id = EXCLUDED.serie_id
    """, (volume.id, title, volume.number, release_date, volume.isbn, volume.possessions_count, volume.image_url,
          serie_id))

    db_conn.commit()
    # print(f"✅ Volume inséré/mis à jour: Volume {volume.number}")


def add_volumes(db_conn, rep_serie_id, current_serie):
    for volume in rep_serie_id.volumes:
        _safe_db_operation(
            lambda v=volume: add_volumes_bdd(db_conn, v, current_serie.id),
            f"de l'ajout du volume {volume.number}"
        )


def add_tasks(rep_serie_id):
    for _ in rep_serie_id.tasks:
        pass  # add_tasks(db_conn, task)


def add_serie(db_conn, rep_serie_id, current_serie):
    if not rep_serie_id.publishers:
        print(f"⚠️ Aucun éditeur trouvé pour la série {current_serie.title}")
        return

    _safe_db_operation(
        lambda: add_series_bdd(db_conn, current_serie, rep_serie_id.publishers[0]),
        f"de l'ajout de la série {current_serie.title}"
    )


def add_publishers(db_conn, rep_serie_id):
    for publisher in rep_serie_id.publishers:
        _safe_db_operation(
            lambda p=publisher: add_publishers_bdd(db_conn, p),
            f"de l'ajout de l'éditeur {publisher.title}"
        )


def add_genres(db_conn, rep_serie_id):
    for genre in rep_serie_id.types:
        _safe_db_operation(
            lambda g=genre: add_genres_bdd(db_conn, g),
            f"de l'ajout du genre {genre.title}"
        )


def add_kinds(db_conn, rep_serie_id):
    for kind in rep_serie_id.kinds:
        _safe_db_operation(
            lambda k=kind: add_kinds_bdd(db_conn, k),
            f"de l'ajout de la catégorie {kind.title}"
        )


def add_authors(db_conn, rep_serie_id):
    for author in rep_serie_id.authors:
        _safe_db_operation(
            lambda a=author: add_authors_bdd(db_conn, a),
            f"de l'ajout de l'auteur {author.name}"
        )


def add_jobs(db_conn, rep_serie_id):
    for job in rep_serie_id.jobs:
        _safe_db_operation(
            lambda j=job: add_jobs_bdd(db_conn, j),
            f"de l'ajout du job {job.title}"
        )


class ProgressTracker:
    """Gestionnaire de progression pour reprendre le traitement après un crash"""

    def __init__(self, progress_file: str = "progress.json"):
        self.progress_file = progress_file
        self.processed_series: Set[str] = set()
        self.load_progress()

    def load_progress(self):
        """Charge la progression depuis le fichier"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    self.processed_series = set(data.get('processed_series', []))
                print(f"📁 Progression chargée: {len(self.processed_series)} séries déjà traitées")
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as load_exc:
            print(f"⚠️ Erreur lors du chargement de la progression: {load_exc}")
        except Exception as load_exc:
            print(f"⚠️ Erreur inattendue lors du chargement: {load_exc}")
            self.processed_series = set()

    def save_progress(self):
        """Sauvegarde la progression dans le fichier"""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump({
                    'processed_series': list(self.processed_series)
                }, f, indent=2)
        except (OSError, IOError) as save_exc:
            print(f"⚠️ Erreur d'accès fichier lors de la sauvegarde: {save_exc}")
        except Exception as save_exc:
            print(f"⚠️ Erreur inattendue lors de la sauvegarde: {save_exc}")

    def is_processed(self, serie_id: str) -> bool:
        """Vérifie si une série a déjà été traitée"""
        return serie_id in self.processed_series

    def mark_processed(self, serie_id: str):
        """Marque une série comme traitée"""
        self.processed_series.add(serie_id)
        self.save_progress()

    def reset(self):
        """Remet à zéro la progression"""
        self.processed_series = set()
        if os.path.exists(self.progress_file):
            os.remove(self.progress_file)
        print("🗑️ Progression réinitialisée")


def process_serie_safely(db_conn, current_serie, serie_endpoint, tracker):
    """Traite une série de manière sécurisée avec gestion d'erreur"""
    try:
        print('\n', current_serie)
        rep_serie_id: SerieEndpointResponse = serie_endpoint.get_serie_by_id_v2(current_serie.id)

        # Traiter les jobs
        add_jobs(db_conn, rep_serie_id)

        # Traiter les auteurs
        add_authors(db_conn, rep_serie_id)

        # Traiter les catégories
        add_kinds(db_conn, rep_serie_id)

        # Traiter les genres
        add_genres(db_conn, rep_serie_id)

        # Traiter les éditeurs
        add_publishers(db_conn, rep_serie_id)

        # Traiter la série
        add_serie(db_conn, rep_serie_id, current_serie)

        # Traiter les tâches (désactivé pour l'instant)
        add_tasks(rep_serie_id)

        # Traiter les volumes
        add_volumes(db_conn, rep_serie_id, current_serie)

        # Marquer la série comme traitée
        tracker.mark_processed(current_serie.id)
        print('----------')
        return True

    except Exception as exc:
        print(
            f"❌ Erreur critique lors du traitement de la série \n {current_serie.id} - {current_serie.title}: \n {exc} \n ==========")
        return False


def _safe_db_operation(operation_func, error_context):
    """Exécute une opération de base de données de manière sécurisée"""
    try:
        operation_func()
    except psycopg2.Error as db_exc:
        print(f"❌ Erreur base de données lors {error_context}: {db_exc}")
    except Exception as exc:
        print(f"❌ Erreur inattendue lors {error_context}: {exc}")


def display_stat_regulierement():
    if (success_count + error_count) % 10 == 0:
        print(
            f"📈 Progression: {success_count} succès, {error_count} erreurs sur {success_count + error_count} nouvelles séries traitées")


if __name__ == '__main__':

    # Initialiser le gestionnaire de progression
    progress_tracker = ProgressTracker()

    try:
        conn = psycopg2.connect(
            database=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USER"),
            host=os.environ.get("DB_HOST"),
            password=os.environ.get("DB_PASSWORD"),
            port=os.environ.get("DB_PORT")
        )
        print("✅ Connexion à la base de données établie")
        time.sleep(2)

        client_anonyme = MangaCollecAPIClient(
            client_id=os.environ.get("CLIENT_ID"),
            client_secret=os.environ.get("CLIENT_SECRET")
        )

        endpoint_serie = SerieEndpoint(client_anonyme)
        reponse_series = endpoint_serie.get_all_series_v2()

        total_series = len(reponse_series.series)
        processed_count = len(progress_tracker.processed_series)
        remaining = total_series - processed_count

        print(f"📊 Total de séries: {total_series}")
        print(f"📊 Séries déjà traitées: {processed_count}")
        print(f"📊 Séries restantes: {remaining}")

        if remaining == 0:
            print("🎉 Toutes les séries ont déjà été traitées!")
        else:
            success_count = 0
            error_count = 0

            for i, serie in enumerate(reponse_series.series, 1):
                # Ignorer les séries déjà traitées
                if progress_tracker.is_processed(serie.id):
                    continue

                print(
                    f"\n🔄 Traitement série {processed_count + success_count + error_count + 1}/{total_series}: {serie.title}")

                if process_serie_safely(conn, serie, endpoint_serie, progress_tracker):
                    success_count += 1
                else:
                    error_count += 1

                # Afficher les statistiques régulièrement
                display_stat_regulierement()

            print("\n🏁 Traitement terminé!")
            print(f"📈 Résumé final: {success_count} succès, {error_count} erreurs")
            print(f"📊 Total traité: {len(progress_tracker.processed_series)}/{total_series} séries")

    except KeyboardInterrupt:
        print("\n⚠️ Interruption utilisateur détectée")
        print(f"📁 Progression sauvegardée: {len(progress_tracker.processed_series)} séries traitées")
        print(RESTART_MESSAGE)

    except psycopg2.Error as db_exc:
        print(f"❌ Erreur critique de base de données: {db_exc}")
        print(f"📁 Progression sauvegardée: {len(progress_tracker.processed_series)} séries traitées")
        print(RESTART_MESSAGE)
    except Exception as exc:
        print(f"❌ Erreur critique inattendue: {exc}")
        print(f"📁 Progression sauvegardée: {len(progress_tracker.processed_series)} séries traitées")
        print(RESTART_MESSAGE)

    finally:
        try:
            if 'conn' in locals():
                conn.close()
                print("🔌 Connexion à la base de données fermée")
        except (psycopg2.Error, AttributeError):
            pass
