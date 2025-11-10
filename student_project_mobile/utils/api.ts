// api.ts
import { Alert } from "react-native";

export const API_BASE = "http://192.168.241.98:8000/api"; // ⚠️ Replace with your system’s IP shown by `ipconfig`

// ----------------------------
// 🔧 Error Parser
// ----------------------------
function parseError(err: any): string {
  if (!err) return "Unknown error";
  if (typeof err === "string") return err;
  if (err.detail) return err.detail;
  if (typeof err === "object") {
    try {
      return Object.values(err)
        .flat()
        .map((v) => (typeof v === "string" ? v : JSON.stringify(v)))
        .join("\n");
    } catch {
      return "Unexpected error format.";
    }
  }
  return "Unknown error";
}

// ----------------------------
// 🌐 GET Request
// ----------------------------
export async function apiGet<T = any>(
  endpoint: string,
  token?: string
): Promise<T | null> {
  try {
    const res = await fetch(`${API_BASE}/${endpoint}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });

    // Check for non-JSON responses
    const text = await res.text();
    let data: any;
    try {
      data = JSON.parse(text);
    } catch {
      data = { detail: text };
    }

    if (!res.ok) throw new Error(parseError(data));
    return data as T;
  } catch (err: any) {
    console.error("❌ apiGet error:", err);
    Alert.alert("Error", err.message || "An unexpected error occurred");
    return null;
  }
}

// ----------------------------
// 🌐 POST Request
// ----------------------------
export async function apiPost<T = any, U = any>(
  endpoint: string,
  data: T,
  token?: string
): Promise<U | null> {
  try {
    const res = await fetch(`${API_BASE}/${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(data),
    });

    const text = await res.text();
    let resData: any;
    try {
      resData = JSON.parse(text);
    } catch {
      resData = { detail: text };
    }

    if (!res.ok) throw new Error(parseError(resData));
    return resData as U;
  } catch (err: any) {
    console.error("❌ apiPost error:", err);
    Alert.alert("Error", err.message || "An unexpected error occurred");
    return null;
  }
}

// ----------------------------
// 🔑 Example Usage
// ----------------------------
// const data = await apiGet("clubs/", token);
// const loginRes = await apiPost("token/", { username, password });
