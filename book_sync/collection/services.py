from typing import Collection

from django.shortcuts import get_object_or_404

from .models import Volume



class CollectionService:

    @staticmethod
    def get_collection_by_id(collection_id):
        """ Recupere une collection par son id """
        try:
            return Collection.objects.get(id=collection_id)
        except Collection.DoesNotExist:
            return None

    @staticmethod
    def get_all_collection(collection_id):
        """ Recupere toutes la collection"""
        return Collection.objects.all().order_by('id')

class VolumeService:
# methode pour le crud d'ajout d'un volume à la collection
    @staticmethod
    def add_volume_to_collection(collection_id, volume_id):
        collection = CollectionService.get_collection_by_id(collection_id)
        volume = Volume.objects.get(id=volume_id)
        collection.add(volume)

    @staticmethod
    def delete_volume_from_collection(volume_id):
        volume = get_object_or_404(Volume, id=volume_id)
        volume.delete()