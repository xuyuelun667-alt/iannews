/**
 * Translate API - Cloudflare Pages Function
 * POST /translate
 * Body: { "text": "string to translate" }
 * Response: { "translated": "翻译后的文本" }
 *
 * 需要在 Cloudflare Dashboard 绑定 AI: 
 *   Pages → iannews → Settings → Functions → AI binding
 *   Variable name: AI
 */

export async function onRequest(context) {
  const { request, env } = context;

  if (request.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json" },
    });
  }

  if (!env.AI) {
    return new Response(JSON.stringify({ error: "AI binding not configured" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }

  try {
    const { text } = await request.json();

    if (!text || typeof text !== "string" || text.length > 2000) {
      return new Response(
        JSON.stringify({ error: "Invalid text (max 2000 chars)" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    // 使用 M2M100 多语言翻译模型
    const result = await env.AI.run("@cf/meta/m2m100-1.2b", {
      text: text,
      source_lang: "english",
      target_lang: "chinese",
    });

    return new Response(JSON.stringify({ translated: result.result || result.translated_text || "" }), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
