// app/lib/api.ts
export const analyzeNews = async (text: string) => {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ news_text: text }),
  });

  if (!res.ok) throw new Error("API Error");
  return res.json();
};
