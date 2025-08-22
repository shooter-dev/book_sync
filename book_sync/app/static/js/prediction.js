const responses = {
    user_age: null,
    user_genre: null,
    user_genre_preference: null,
    user_category_preference: null,
    user_comment: null
};

function nextStep(nextId) {
    document.querySelectorAll('[id^="step-"]').forEach(el => el.classList.add('hidden'));
    document.getElementById(nextId).classList.remove('hidden');
}

function updateRecap() {
    const recapList = document.getElementById("recap-list");
    recapList.innerHTML = "";

    const labels = {
        user_age: "Âge",
        user_genre: "Genre",
        user_genre_preference: "Genre préféré",
        user_category_preference: "Catégorie préférée",
        user_comment: "Commentaire"
    };

    Object.entries(responses).forEach(([key, value]) => {
        if (value !== null && value !== "") {
            const item = document.createElement("div");
            item.className = "flex justify-between items-center bg-gray-100 dark:bg-gray-700 p-4 rounded-lg";

            item.innerHTML = `
                <span class="text-gray-800 dark:text-white font-medium">${labels[key]} : ${value}</span>
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
        user_comment: "step-final"
    };

    nextStep(stepMap[field]);

    // Pré-remplissage du champ commentaire
    if (field === "user_comment") {
        document.getElementById("user_comment").value = responses.user_comment || "";
    }
}


// Gestion des réponses
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("user_age").addEventListener("change", (e) => {
        responses.user_age = e.target.value;
        updateRecap();
    });

document.getElementById("user_age").addEventListener("change", (e) => {
    responses.user_age = e.target.value;
    updateRecap();

    // Si le genre n’a pas encore été rempli, on l’affiche
    if (!responses.user_genre) {
        nextStep("step-gender");
    } else if (!responses.user_genre_preference) {
        nextStep("step-genre-preference");
    } else if (!responses.user_category_preference) {
        nextStep("step-category-preference");
    } else if (!responses.user_comment) {
        nextStep("step-final");
    }
});


    document.querySelectorAll('.response-btn').forEach(btn => {
        btn.classList.add('bg-gray-200', 'dark:bg-gray-700', 'text-gray-800', 'dark:text-gray-200', 'py-2', 'px-4', 'rounded-lg', 'hover:bg-gray-300', 'dark:hover:bg-gray-600', 'transition');
        btn.addEventListener('click', () => {
            const currentStep = btn.closest('[id^="step-"]');
            const stepId = currentStep.id;

            const keyMap = {
                "step-gender": "user_genre",
                "step-genre-preference": "user_genre_preference",
                "step-category-preference": "user_category_preference"
            };

            const nextMap = {
                "step-gender": "step-genre-preference",
                "step-genre-preference": "step-category-preference",
                "step-category-preference": "step-final"
            };

            const key = keyMap[stepId];
            const next = nextMap[stepId];

            if (key) {
                responses[key] = btn.textContent.trim();
                updateRecap();
                nextStep(next);
            }
        });
    });
});
