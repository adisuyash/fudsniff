const baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

export const analyzeNews = async (text: string) => {
  try {
    const res = await fetch(`${baseURL}/api/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ news_text: text }),
    });

    if (!res.ok) {
      const errorBody = await res.text();
      throw new Error(
        `API Error: ${res.status} ${res.statusText} — ${errorBody}`
      );
    }

    return await res.json();
  } catch (error) {
    console.error("Failed to analyze news:", error);
    throw error;
  }
};

export const fetchManualSignals = async () => {
  try {
    const res = await fetch(`${baseURL}/api/manual/signals`);
    if (!res.ok) {
      throw new Error("Failed to fetch manual signals");
    }
    const data = await res.json();
    return data.signals || [];
  } catch (error) {
    console.error("Error loading manual signals:", error);
    return [];
  }
};
