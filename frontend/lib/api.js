const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(options.headers || {}),
    },
  });

  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message = typeof data === "string" ? data : data?.detail || data?.message || "Request failed";
    throw new Error(message);
  }

  return data;
}

export async function syncUser(payload) {
  return request("/user/sync", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export async function uploadPdf(file, userId) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("user_id", userId);

  return request("/upload", {
    method: "POST",
    body: formData,
  });
}

export async function queryDocument(payload) {
  return request("/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export async function getChats(userId) {
  return request(`/chats?user_id=${encodeURIComponent(userId)}`);
}

export async function getMessages(chatId) {
  return request(`/message/${encodeURIComponent(chatId)}`);
}

export async function getDocuments(userId) {
  return request(`/documents?user_id=${encodeURIComponent(userId)}`);
}