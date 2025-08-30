push-azur:
	docker tag app-booksync booksyncrepo.azurecr.io/app-booksync
	docker buildx build --no-cache --platform linux/amd64 -t app-booksync:latest .
	docker push booksyncrepo.azurecr.io/app-booksync
	az containerapp update \
	  --name app-booksync \
	  --resource-group vplatevoetRG \
	  --image booksyncrepo.azurecr.io/app-booksync:latest
