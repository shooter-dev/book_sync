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

    if (nextId === 'step-genre-preference') {
        syncSelectionStyles('genre');
    } else if (nextId === 'step-category-preference') {
        syncSelectionStyles('kind');
    } else if (nextId === 'step-prediction-type') {
        // aucune action spécifique pour le moment
    } else if (nextId === 'step-final') {
        const textarea = document.getElementById('user_comment');
        if (textarea) textarea.value = responses.user_comment || '';
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
});



function submitToFastAPI() {
const rawCollection = document.getElementById("collection_data").value;
let collection = {};

if (rawCollection && rawCollection.trim() !== "") {
  try {
    collection = JSON.parse(rawCollection);
  } catch (e) {
    console.error("❌ Erreur de parsing JSON:", e);
  }
} else {
  console.warn("⚠️ Le champ collection_data est vide");
}

//console.log(JSON.parse(document.getElementById("read_data").value))
console.log(JSON.parse(document.getElementById("collection_data").value))

const payload = {
  user_age: parseInt(responses.user_age),
  user_genre: responses.user_genre,
  genre_preference: responses.user_genre_preference.join(","),
  category_preference: responses.user_category_preference.join(","),
  user_comment: responses.user_comment,
  prediction_type: responses.prediction_type,
  user_id: document.getElementById("user_id").value,
  //collection : JSON.parse(document.getElementById("collection_data").value),
  read : JSON.parse(document.getElementById("read_data").value)
};

console.log("📦 Collection :", collection);
console.log("📖 Read :", read);

const queryString = Object.entries(payload)
  .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
  .join("&");

//window.location.href = `http://127.0.0.1:8001/predict/result?${queryString}`
}

