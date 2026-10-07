export async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(path, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...options.headers },
    });
  } catch {
    throw new Error('Cannot reach TaskBoard. Check your connection and try again.');
  }
  if (!response.ok) {
    let data;
    try { data = await response.json(); } catch { /* proxy responses may not be JSON */ }
    const message = typeof data?.detail === 'string' ? data.detail :
      response.status === 422 ? 'Check the task details and try again.' :
      response.status >= 500 ? 'TaskBoard is temporarily unavailable. Try again shortly.' :
      'The request could not be completed. Refresh the board and try again.';
    throw new Error(message);
  }
  return response.status === 204 ? null : response.json();
}
