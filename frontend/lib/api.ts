import { supabase } from "./supabase";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  // Get active session
  const sessionRes = await supabase.auth.getSession();
  const token = sessionRes.data.session?.access_token;

  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");
  
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : "/" + endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errBody = await response.json().catch(() => ({}));
      const errorMsg = errBody?.error?.message || response.statusText || "Request failed";
      const errorSuggestion = errBody?.error?.suggestion || "Please try again later.";
      const errorCode = errBody?.error?.code || "API_ERROR";
      
      const error = new Error(errorMsg) as any;
      error.status = response.status;
      error.suggestion = errorSuggestion;
      error.code = errorCode;
      throw error;
    }

    return await response.json();
  } catch (err: any) {
    if (err.status) {
      throw err;
    }
    
    const isProduction = API_BASE_URL.includes("onrender.com") || 
      (!API_BASE_URL.includes("localhost") && !API_BASE_URL.includes("127.0.0.1"));
      
    const errorMsg = isProduction
      ? "Failed to connect to backend server. The service might be waking up."
      : "Failed to connect to backend server. Make sure it is running on port 8000.";
      
    const errorSuggestion = isProduction
      ? "Free instances on Render automatically spin down after inactivity. The first request can take up to 50 seconds to wake the server up. Please try again in a few moments."
      : "Start the FastAPI server by running 'uvicorn app.main:app --port 8000' inside the backend folder.";

    // Network or server offline error
    const netErr = new Error(errorMsg) as any;
    netErr.status = 503;
    netErr.code = "SERVER_OFFLINE";
    netErr.suggestion = errorSuggestion;
    throw netErr;
  }
}
