# import pytest
# from fastapi.testclient import TestClient
# from main import app
# import json

# client = TestClient(app)

# class TestPredictEndpoint:
#     """Tests pour l'endpoint de prédiction FastAPI"""
    
#     def test_predict_endpoint_success(self):
#         """Test de l'endpoint predict avec des données valides"""
#         # Données de test valides
#         form_data = {
#             "user_age": "25",
#             "user_genre": "Homme",
#             "genre_preference": "Science Fiction,Fantasy",
#             "category_preference": "Manga,Light Novel",
#             "user_comment": "J'aimerais découvrir de nouveaux genres",
#             "prediction_type": "collection",
#             "collection": json.dumps({
#                 "One Piece": {
#                     "volumes": {"1": "vol-id-1", "2": "vol-id-2"},
#                     "id_series": "series-id-1"
#                 }
#             }),
#             "read": json.dumps({
#                 "Attack on Titan": {
#                     "volumes": {"1": "vol-id-3"},
#                     "id_series": "series-id-2"
#                 }
#             }),
#             "user_mood": "Joyeux",
#             "csrfmiddlewaretoken": "test-csrf-token"
#         }
        
#         response = client.post("/predict/", data=form_data)
        
#         assert response.status_code == 200
#         response_data = response.json()
        
#         # Vérifier la structure de la réponse
#         assert "status" in response_data
#         assert response_data["status"] == "success"
#         assert "user_age" in response_data
#         assert "user_genre" in response_data
#         assert "genre_preference" in response_data
#         assert "category_preference" in response_data
#         assert "user_comment" in response_data
#         assert "prediction_type" in response_data
#         assert "collection" in response_data
#         assert "read" in response_data
#         assert "user_mood" in response_data
        
#         # Vérifier les valeurs
#         assert response_data["user_age"] == "25"
#         assert response_data["user_genre"] == "Homme"
#         assert response_data["genre_preference"] == ["Science Fiction", "Fantasy"]
#         assert response_data["category_preference"] == ["Manga", "Light Novel"]
#         assert response_data["user_comment"] == "J'aimerais découvrir de nouveaux genres"
#         assert response_data["prediction_type"] == "collection"
#         assert response_data["user_mood"] == "Joyeux"
        
#         # Vérifier les données de collection et lecture
#         assert isinstance(response_data["collection"], dict)
#         assert isinstance(response_data["read"], dict)
#         assert "One Piece" in response_data["collection"]
#         assert "Attack on Titan" in response_data["read"]
    
#     def test_predict_endpoint_empty_preferences(self):
#         """Test avec des préférences vides"""
#         form_data = {
#             "user_age": "30",
#             "user_genre": "Femme",
#             "genre_preference": "",
#             "category_preference": "",
#             "user_comment": "",
#             "prediction_type": "proposition",
#             "collection": "{}",
#             "read": "{}",
#             "user_mood": "Triste",
#             "csrfmiddlewaretoken": "test-csrf-token"
#         }
        
#         response = client.post("/predict/", data=form_data)
        
#         assert response.status_code == 200
#         response_data = response.json()
        
#         assert response_data["status"] == "success"
#         assert response_data["genre_preference"] == []
#         assert response_data["category_preference"] == []
#         assert response_data["user_comment"] == ""
#         assert response_data["collection"] == {}
#         assert response_data["read"] == {}
    
#     def test_predict_endpoint_invalid_json_collection(self):
#         """Test avec JSON invalide pour la collection"""
#         form_data = {
#             "user_age": "25",
#             "user_genre": "Homme",
#             "genre_preference": "Action",
#             "category_preference": "Manga",
#             "user_comment": "Test",
#             "prediction_type": "collection",
#             "collection": "invalid json",
#             "read": "{}",
#             "user_mood": "Joyeux",
#             "csrfmiddlewaretoken": "test-csrf-token"
#         }
        
#         response = client.post("/predict/", data=form_data)
        
#         assert response.status_code == 400
#         response_data = response.json()
        
#         assert "error" in response_data
#         assert "JSON invalide" in response_data["error"]
#         assert "collection" in response_data
#         assert "read" in response_data
    
#     def test_predict_endpoint_invalid_json_read(self):
#         """Test avec JSON invalide pour les lectures"""
#         form_data = {
#             "user_age": "25",
#             "user_genre": "Homme",
#             "genre_preference": "Action",
#             "category_preference": "Manga",
#             "user_comment": "Test",
#             "prediction_type": "collection",
#             "collection": "{}",
#             "read": "invalid json",
#             "user_mood": "Joyeux",
#             "csrfmiddlewaretoken": "test-csrf-token"
#         }
        
#         response = client.post("/predict/", data=form_data)
        
#         assert response.status_code == 400
#         response_data = response.json()
        
#         assert "error" in response_data
#         assert "JSON invalide" in response_data["error"]
    
#     def test_predict_endpoint_missing_required_fields(self):
#         """Test avec des champs requis manquants"""
#         # Test sans user_age
#         response = client.post("/predict/", data={
#             "user_genre": "Homme",
#             "genre_preference": "Action",
#             "category_preference": "Manga",
#             "user_comment": "Test",
#             "prediction_type": "collection",
#             "collection": "{}",
#             "read": "{}",
#             "user_mood": "Joyeux",
#             "csrfmiddlewaretoken": "test-csrf-token"
#         })
        
#         assert response.status_code == 422  # Unprocessable Entity
    
#     def test_predict_endpoint_complex_data(self):
#         """Test avec des données complexes"""
#         complex_collection = {
#             "One Piece": {
#                 "volumes": {"1": "vol-1", "2": "vol-2", "3": "vol-3"},
#                 "id_series": "series-1"
#             },
#             "Naruto": {
#                 "volumes": {"1": "vol-4", "5": "vol-5", "10": "vol-6"},
#                 "id_series": "series-2"
#             },
#             "Dragon Ball": {
#                 "volumes": {"1": "vol-7", "2": "vol-8"},
#                 "id_series": "series-3"
#             }
#         }
        
#         complex_read = {
#             "Death Note": {
#                 "volumes": {"1": "vol-9", "2": "vol-10", "3": "vol-11"},
#                 "id_series": "series-4"
#             }
#         }
        
#         form_data = {
#             "user_age": "28",
#             "user_genre": "Non binaire",
#             "genre_preference": "Thriller,Horror,Mystery",
#             "category_preference": "Manga,Manhwa,Light Novel,Roman,BD",
#             "user_comment": "Je cherche quelque chose de sombre et psychologique",
#             "prediction_type": "proposition",
#             "collection": json.dumps(complex_collection),
#             "read": json.dumps(complex_read),
#             "user_mood": "Énervé",
#             "csrfmiddlewaretoken": "test-csrf-token"
#         }
        
#         response = client.post("/predict/", data=form_data)
        
#         assert response.status_code == 200
#         response_data = response.json()
        
#         assert response_data["status"] == "success"
#         assert len(response_data["genre_preference"]) == 3
#         assert len(response_data["category_preference"]) == 5
#         assert response_data["collection"] == complex_collection
#         assert response_data["read"] == complex_read
    
#     def test_predict_endpoint_special_characters(self):
#         """Test avec des caractères spéciaux"""
#         form_data = {
#             "user_age": "22",
#             "user_genre": "Femme",
#             "genre_preference": "Science-Fiction,Fantastique",
#             "category_preference": "Manga,Light Novel",
#             "user_comment": "J'aimerais des histoires avec des émotions fortes et des personnages complexes ! 😊",
#             "prediction_type": "collection",
#             "collection": json.dumps({
#                 "L'Attaque des Titans": {
#                     "volumes": {"1": "vol-1", "2": "vol-2"},
#                     "id_series": "series-1"
#                 }
#             }),
#             "read": "{}",
#             "user_mood": "Sentimental",
#             "csrfmiddlewaretoken": "test-csrf-token"
#         }
        
#         response = client.post("/predict/", data=form_data)
        
#         assert response.status_code == 200
#         response_data = response.json()
        
#         assert response_data["status"] == "success"
#         assert "😊" in response_data["user_comment"]
#         assert "L'Attaque des Titans" in response_data["collection"]

# class TestPredictDataValidation:
#     """Tests pour la validation des données"""
    
#     def test_genre_preference_parsing(self):
#         """Test du parsing des préférences de genre"""
#         form_data = {
#             "user_age": "25",
#             "user_genre": "Homme",
#             "genre_preference": "Action,Adventure,Comedy",
#             "category_preference": "Manga",
#             "user_comment": "",
#             "prediction_type": "collection",
#             "collection": "{}",
#             "read": "{}",
#             "user_mood": "Joyeux",
#             "csrfmiddlewaretoken": "test-csrf-token"
#         }
        
#         response = client.post("/predict/", data=form_data)
#         response_data = response.json()
        
#         assert isinstance(response_data["genre_preference"], list)
#         assert len(response_data["genre_preference"]) == 3
#         assert "Action" in response_data["genre_preference"]
#         assert "Adventure" in response_data["genre_preference"]
#         assert "Comedy" in response_data["genre_preference"]
    
#     def test_category_preference_parsing(self):
#         """Test du parsing des préférences de catégorie"""
#         form_data = {
#             "user_age": "25",
#             "user_genre": "Homme",
#             "genre_preference": "Action",
#             "category_preference": "Manga,Light Novel,Manhwa,Webtoon",
#             "user_comment": "",
#             "prediction_type": "collection",
#             "collection": "{}",
#             "read": "{}",
#             "user_mood": "Joyeux",
#             "csrfmiddlewaretoken": "test-csrf-token"
#         }
        
#         response = client.post("/predict/", data=form_data)
#         response_data = response.json()
        
#         assert isinstance(response_data["category_preference"], list)
#         assert len(response_data["category_preference"]) == 4
#         assert "Manga" in response_data["category_preference"]
#         assert "Light Novel" in response_data["category_preference"]
#         assert "Manhwa" in response_data["category_preference"]
#         assert "Webtoon" in response_data["category_preference"]
    
#     def test_json_data_parsing(self):
#         """Test du parsing des données JSON"""
#         collection_data = {
#             "Test Serie": {
#                 "volumes": {"1": "volume-id-1", "2": "volume-id-2"},
#                 "id_series": "series-id-1"
#             }
#         }
        
#         form_data = {
#             "user_age": "25",
#             "user_genre": "Homme",
#             "genre_preference": "Action",
#             "category_preference": "Manga",
#             "user_comment": "",
#             "prediction_type": "collection",
#             "collection": json.dumps(collection_data),
#             "read": "{}",
#             "user_mood": "Joyeux",
#             "csrfmiddlewaretoken": "test-csrf-token"
#         }
        
#         response = client.post("/predict/", data=form_data)
#         response_data = response.json()
        
#         assert response_data["collection"] == collection_data
#         assert isinstance(response_data["collection"], dict)
#         assert "Test Serie" in response_data["collection"]
#         assert "volumes" in response_data["collection"]["Test Serie"]
#         assert "id_series" in response_data["collection"]["Test Serie"]

# if __name__ == "__main__":
#     pytest.main([__file__])