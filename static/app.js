const textInput = document.getElementById("text-input");
const analyzeBtn = document.getElementById("analyze-btn");
const fillExampleBtn = document.getElementById("fill-example-btn");
const statusEl = document.getElementById("status");

const emptyState = document.getElementById("empty-state");
const resultContent = document.getElementById("result-content");

const predictedClassEl = document.getElementById("predicted-class");
const overallScoreEl = document.getElementById("overall-score");
const modelExplanationEl = document.getElementById("model-explanation");

const probabilitiesEl = document.getElementById("probabilities");
const readabilityScoreEl = document.getElementById("readability-score");
const emotionalScoreEl = document.getElementById("emotional-score");
const engagementScoreEl = document.getElementById("engagement-score");

const keywordsEl = document.getElementById("keywords");
const strengthsEl = document.getElementById("strengths");
const weaknessesEl = document.getElementById("weaknesses");
const recommendationsEl = document.getElementById("recommendations");
const featureSummaryEl = document.getElementById("feature-summary");

fillExampleBtn.addEventListener("click", () => {
    textInput.value = "Устали что Ваш телефон слишком быстро разряжается!? Смартфон с батареей, которая держится до двух дней без подзарядки и помогает оставаться на связи без лишних ограничений";
});

analyzeBtn.addEventListener("click", async () => {
    const text = textInput.value.trim();

    if (!text) {
        statusEl.textContent = "Введите текст для анализа.";
        return;
    }

    statusEl.textContent = "Идёт анализ...";
    analyzeBtn.disabled = true;

    try {
        const response = await fetch("/analyze-advanced", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ text })
        });

        if (!response.ok) {
            throw new Error("Не удалось выполнить анализ.");
        }

        const data = await response.json();
        renderResult(data);
        statusEl.textContent = "Анализ завершён.";
    } catch (error) {
        statusEl.textContent = error.message;
    } finally {
        analyzeBtn.disabled = false;
    }
});

function renderResult(data) {
    emptyState.classList.add("hidden");
    resultContent.classList.remove("hidden");

    predictedClassEl.textContent = data.predicted_class;
    overallScoreEl.textContent = formatNumber(data.overall_score);
    modelExplanationEl.textContent = data.model_explanation || "—";

    readabilityScoreEl.textContent = formatNumber(data.readability_score);
    emotionalScoreEl.textContent = formatNumber(data.emotional_score);
    engagementScoreEl.textContent = formatNumber(data.engagement_score);

    renderProbabilities(data.probabilities || {});
    renderTags(keywordsEl, data.top_keywords || []);
    renderList(strengthsEl, data.strengths || []);
    renderList(weaknessesEl, data.weaknesses || []);
    renderList(recommendationsEl, data.recommendations || []);
    renderFeatureSummary(data.feature_summary || {});
}

function renderProbabilities(probabilities) {
    probabilitiesEl.innerHTML = "";

    Object.entries(probabilities)
        .sort((a, b) => b[1] - a[1])
        .forEach(([label, value]) => {
            const wrapper = document.createElement("div");
            wrapper.className = "prob-item";

            const labelRow = document.createElement("div");
            labelRow.className = "prob-label";
            labelRow.innerHTML = `<span>${label}</span><span>${(value * 100).toFixed(1)}%</span>`;

            const bar = document.createElement("div");
            bar.className = "prob-bar";

            const fill = document.createElement("div");
            fill.className = "prob-fill";
            fill.style.width = `${Math.max(0, Math.min(value * 100, 100))}%`;

            bar.appendChild(fill);
            wrapper.appendChild(labelRow);
            wrapper.appendChild(bar);
            probabilitiesEl.appendChild(wrapper);
        });
}

function renderTags(container, items) {
    container.innerHTML = "";

    if (!items.length) {
        container.textContent = "Нет данных.";
        return;
    }

    items.forEach((item) => {
        const tag = document.createElement("span");
        tag.className = "tag";
        tag.textContent = item;
        container.appendChild(tag);
    });
}

function renderList(container, items) {
    container.innerHTML = "";

    if (!items.length) {
        const li = document.createElement("li");
        li.textContent = "Нет данных.";
        container.appendChild(li);
        return;
    }

    items.forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item;
        container.appendChild(li);
    });
}

function renderFeatureSummary(summary) {
    featureSummaryEl.innerHTML = "";

    const entries = [
        ["Количество слов", summary.text_length],
        ["Читаемость", summary.readability_level],
        ["Вовлечение", summary.engagement_level],
        ["Эмоциональность", summary.emotional_level],
        ["Есть вопрос", formatBoolean(summary.has_question)],
        ["Есть CTA", formatBoolean(summary.has_cta)]
    ];

    entries.forEach(([label, value]) => {
        const item = document.createElement("div");
        item.className = "summary-item";
        item.innerHTML = `<strong>${label}</strong><span>${value ?? "—"}</span>`;
        featureSummaryEl.appendChild(item);
    });
}

function formatNumber(value) {
    if (typeof value !== "number") return "—";
    return value.toFixed(3);
}

function formatBoolean(value) {
    if (value === true) return "Да";
    if (value === false) return "Нет";
    return "—";
}