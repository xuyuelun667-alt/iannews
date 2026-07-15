// 屏蔽中国大陆 IP 访问
// 在 Cloudflare Pages Functions 环境中自动运行
// 通过 CF-IPCountry 请求头判断来源地区

/**
 * @param {import('@cloudflare/workers-types').PagesFunctionContext} context
 * @returns {Promise<Response>}
 */
export async function onRequest(context) {
  // context.request.cf 由 Cloudflare 注入，包含地理位置信息
  const country = context.request.cf?.country;

  if (country === 'CN') {
    return new Response(
      'Access Denied: This service is not available in your region.',
      {
        status: 403,
        headers: {
          'Content-Type': 'text/plain; charset=utf-8',
        },
      }
    );
  }

  // 非中国大陆流量正常放行
  return context.next();
}
