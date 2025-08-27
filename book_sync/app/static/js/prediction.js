const responses = {
    user_age: null,
    user_genre: null,
    user_genre_preference: [],
    user_category_preference: [],
    user_comment: null,
    prediction_type: null
};

function nextStep(nextId) {
    document.querySelectorAll('[id^="step-"]').forEach(el => el.classList.add('hidden'));
    const target = document.getElementById(nextId);
    if (target) target.classList.remove('hidden');

    syncHiddenFields();

    if (nextId === 'step-genre-preference') {
        syncSelectionStyles('genre');
    } else if (nextId === 'step-category-preference') {
        syncSelectionStyles('kind');
    } else if (nextId === 'step-prediction-type') {
        // aucune action spécifique pour le moment
    } else if (nextId === 'step-final') {
        const textarea = document.getElementById('user_comment');
        if (textarea) textarea.value = responses.user_comment || '';
    } else if (nextId === 'step-comment') {
        updateRecap(); // ✅ affiche le récapitulatif dynamique
    }
}

function syncSelectionStyles(type) {
    if (type === 'genre') {
        const selected = new Set(responses.user_genre_preference);
        document.querySelectorAll('.genre-btn').forEach(btn => {
            setBtnSelected(btn, selected.has(btn.textContent.trim()));
        });
        document.getElementById('genre-count').textContent = responses.user_genre_preference.length;
    } else if (type === 'kind') {
        const selected = new Set(responses.user_category_preference);
        document.querySelectorAll('.kind-btn').forEach(btn => {
            setBtnSelected(btn, selected.has(btn.textContent.trim()));
        });
        document.getElementById('kind-count').textContent = responses.user_category_preference.length;
    }
}

function setBtnSelected(btn, isSelected) {
    if (isSelected) {
        btn.classList.add('bg-red-600', 'text-white');
        btn.classList.remove('bg-gray-200', 'dark:bg-gray-700');
    } else {
        btn.classList.remove('bg-red-600', 'text-white');
        btn.classList.add('bg-gray-200', 'dark:bg-gray-700');
    }
}

function updateRecap() {
    const recapList = document.getElementById("recap-list");
    recapList.innerHTML = "";

    const labels = {
        user_age: "Âge",
        user_genre: "Genre",
        user_genre_preference: "Genres préférés",
        user_category_preference: "Catégories préférées",
        user_comment: "Commentaire",
        prediction_type: "Type de prédiction"
    };

    Object.entries(responses).forEach(([key, value]) => {
        if (value !== null && value !== "" && (!Array.isArray(value) || value.length !== 0)) {
            const item = document.createElement("div");
            item.className = "flex justify-between items-center bg-gray-100 dark:bg-gray-700 p-4 rounded-lg";

            let displayValue = Array.isArray(value) ? value.join(', ') : value;

            item.innerHTML = `
                <span class="text-gray-800 dark:text-white font-medium">${labels[key]} : ${displayValue}</span>
                <button onclick="modifyField('${key}')" class="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 transition">Modifier</button>
            `;
            recapList.appendChild(item);
        }
    });
}

function modifyField(field) {
    const stepMap = {
        user_age: "step-age",
        user_genre: "step-gender",
        user_genre_preference: "step-genre-preference",
        user_category_preference: "step-category-preference",
        prediction_type: "step-prediction-type",
        user_comment: "step-final"
    };
    nextStep(stepMap[field]);
}

function validateAgeAndContinue() {
    const ageInput = document.getElementById('user_age');
    if (responses.user_age) {
        nextStep('step-gender');
        updateRecap();
        return;
    }
    if (!ageInput || !ageInput.value) {
        alert('Veuillez entrer votre âge');
        return;
    }
    responses.user_age = ageInput.value;
    saveAge();
}

function modifyAge() {
    const ageStep = document.getElementById('step-age');
    ageStep.innerHTML = `
        <label for="user_age" class="block text-lg font-medium text-gray-900 dark:text-white mb-2">Quel est votre âge ?</label>
        <input type="number" id="user_age" name="user_age" min="1" max="100" required value="${responses.user_age || ''}"
               class="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 dark:bg-gray-900 dark:text-white">
        <button onclick="saveAge()" class="mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition">Valider</button>
    `;
    document.getElementById('user_age').addEventListener('change', e => {
        responses.user_age = e.target.value;
        updateRecap();
    });
}

function saveAge() {
    fetch('/prediction/save-age/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ age: responses.user_age })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            nextStep('step-gender');
            updateRecap();
        } else {
            alert('Erreur lors de la sauvegarde de l\'âge');
        }
    })
    .catch(() => alert('Erreur réseau lors de la sauvegarde de l\'âge'));
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        document.cookie.split(';').forEach(cookie => {
            const c = cookie.trim();
            if (c.startsWith(name + '=')) cookieValue = decodeURIComponent(c.slice(name.length + 1));
        });
    }
    return cookieValue;
}

document.addEventListener("DOMContentLoaded", () => {
    const ageInput = document.getElementById("user_age");
    if (ageInput) ageInput.addEventListener("change", e => {
        responses.user_age = e.target.value;
        updateRecap();
    });

    document.querySelectorAll('.response-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            responses.user_genre = btn.textContent.trim();
            updateRecap();
            nextStep("step-genre-preference");
        });
    });

    document.querySelectorAll('.genre-btn, .kind-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const isGenre = btn.classList.contains('genre-btn');
            const key = isGenre ? 'user_genre_preference' : 'user_category_preference';
            const max = isGenre ? 3 : 5;
            const value = btn.textContent.trim();
            const arr = responses[key];
            const already = arr.includes(value);

            if (already) {
                responses[key] = arr.filter(v => v !== value);
                setBtnSelected(btn, false);
            } else {
                if (arr.length >= max) {
                    alert(`Vous pouvez sélectionner jusqu'à ${max} ${isGenre ? 'genres' : 'catégories'} maximum.`);
                    return;
                }
                arr.push(value);
                setBtnSelected(btn, true);
            }

            if (isGenre) {
                document.getElementById('genre-count').textContent = responses.user_genre_preference.length;
            } else {
                document.getElementById('kind-count').textContent = responses.user_category_preference.length;
            }

            updateRecap();
        });
    });

    const validateGenreBtn = document.getElementById('validate-genre-btn');
    if (validateGenreBtn) {
        validateGenreBtn.addEventListener('click', () => {
            const n = responses.user_genre_preference.length;
            if (n < 1 || n > 3) {
                alert("Veuillez sélectionner entre 1 et 3 genres.");
                return;
            }
            nextStep('step-category-preference');
        });
    }

    const validateCategoryBtn = document.getElementById('validate-category-btn');
    if (validateCategoryBtn) {
        validateCategoryBtn.addEventListener('click', () => {
            const n = responses.user_category_preference.length;
            if (n < 1 || n > 5) {
                alert("Veuillez sélectionner entre 1 et 5 catégories.");
                return;
            }
            nextStep('step-prediction-type');
        });
    }

    const predictionBtns = document.querySelectorAll('.prediction-type-btn');
    predictionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            responses.prediction_type = btn.getAttribute('data-type');
            updateRecap();
            nextStep('step-final');
        });
    });

    const comment = document.getElementById('user_comment');
    if (comment) comment.addEventListener('input', e => {
        responses.user_comment = e.target.value;
        updateRecap();
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const userAgeFromDB = parseInt("{{ user_age|default:'0' }}");
    if (userAgeFromDB > 0) {
        responses.user_age = userAgeFromDB;
        updateRecap();
        nextStep('step-gender');
    } else {
        nextStep('step-age');
    }
    const ageInput = document.getElementById("user_age");
    if (ageInput) {
        ageInput.addEventListener("change", e => {
            responses.user_age = e.target.value;
            updateRecap();
        });
    }

    // ✅ CORRECTION : Récupération des données Django existantes
    const collectionInput = document.getElementById("user_collection");
    const readInput = document.getElementById("prediction_read");

    console.log("Collection input value:", collectionInput ? collectionInput.value : "N/A");
    console.log("Read input value:", readInput ? readInput.value : "N/A");
});

// ✅ FONCTION CORRIGÉE : syncHiddenFields
function syncHiddenFields() {
    // Mise à jour des champs de formulaire
    document.getElementById("user_age_hidden").value = responses.user_age || "";
    document.getElementById("user_genre_hidden").value = responses.user_genre || "";
    document.getElementById("genre_preference_hidden").value = responses.user_genre_preference.join(",") || "";
    document.getElementById("category_preference_hidden").value = responses.user_category_preference.join(",") || "";
    document.getElementById("user_comment_hidden").value = responses.user_comment || "";
    document.getElementById("prediction_type_hidden").value = responses.prediction_type || "";



    console.log("Champs cachés synchronisés:", {
        age: responses.user_age,
        genre: responses.user_genre,
        genre_pref: responses.user_genre_preference,
        category_pref: responses.user_category_preference,
        comment: responses.user_comment,
        prediction_type: responses.prediction_type
    });
}

// ✅ FONCTION DE DEBUG pour vérifier les données
function debugFormData() {
    const formData = new FormData(document.getElementById('prediction-form'));

    console.log("=== DONNÉES DU FORMULAIRE ===");
    for (let [key, value] of formData.entries()) {
        console.log(`${key}: ${value}`);
    }

    // Vérification spéciale des données JSON
    const collectionValue = formData.get('collection');
    const readValue = formData.get('read');

    if (collectionValue) {
        try {
            const collectionData = JSON.parse(collectionValue);
            console.log("Collection parsée:", collectionData);
        } catch (e) {
            console.error("Erreur parsing collection:", e);
        }
    }

    if (readValue) {
        try {
            const readData = JSON.parse(readValue);
            console.log("Read parsée:", readData);
        } catch (e) {
            console.error("Erreur parsing read:", e);
        }
    }
}

// Ajout d'un bouton de debug (optionnel, pour tes tests)
document.addEventListener("DOMContentLoaded", () => {
    // Ajouter un bouton de debug en bas de page
    const debugBtn = document.createElement('button');
    debugBtn.textContent = '🐛 Debug Form Data';
    debugBtn.type = 'button';
    debugBtn.className = 'fixed bottom-4 right-4 bg-yellow-500 text-black px-4 py-2 rounded shadow-lg hover:bg-yellow-600';
    debugBtn.onclick = debugFormData;
    document.body.appendChild(debugBtn);
});

document.addEventListener("DOMContentLoaded", () => {
    const initialCollection = JSON.parse(document.getElementById('collection-data').textContent);
    const initialRead = JSON.parse(document.getElementById('read-data').textContent);

    const collectionInput = document.getElementById("user_collection");
    const readInput = document.getElementById("prediction_read");

    if (collectionInput) collectionInput.value = JSON.stringify(initialCollection);
    if (readInput) readInput.value = JSON.stringify(initialRead);

    console.log("Collection initiale injectée:", collectionInput.value);
    console.log("Read initial injecté:", readInput.value);
});

document.getElementById("prediction-form").addEventListener("submit", function() {
    syncHiddenFields(); // met à jour les autres champs dynamiques

    // Collection et Read restent injectés
    console.log("🚀 FormData prêt à envoyer :", {
        collection: document.getElementById("user_collection").value,
        read: document.getElementById("prediction_read").value
    });
});