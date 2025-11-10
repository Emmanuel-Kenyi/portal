import React, { useState } from "react";
import {
  View,
  TextInput,
  TouchableOpacity,
  Text,
  StyleSheet,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { useAuth } from "../context/AuthContext";
import { apiPost } from "../utils/api";

interface LoginResponse {
  access: string;
  refresh: string;
  role: "admin" | "lecturer" | "student";
  username: string;
  user_id: number;
}

export default function LoginScreen() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleLogin = async () => {
    if (!username || !password) {
      Alert.alert("Error", "Please enter both username and password");
      return;
    }

    setLoading(true);

    try {
      const data = await apiPost<{ username: string; password: string }, LoginResponse>(
        "token/",
        { username, password }
      );

      if (data) {
        await login({
          token: data.access,
          refresh: data.refresh,
          role: data.role,
          username: data.username,
          id: data.user_id,
        });
      } else {
        // apiPost already showed an Alert, just log for debugging
        console.log("Login failed - no data returned");
      }
    } catch (error) {
      console.error("Unexpected login error:", error);
      Alert.alert("Error", "An unexpected error occurred");
    } finally {
      // ✅ This ensures loading stops no matter what
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      style={styles.container}
    >
      <View style={styles.loginCard}>
        <Text style={styles.title}>Login</Text>

        <TextInput
          placeholder="Username"
          value={username}
          onChangeText={setUsername}
          style={styles.input}
          editable={!loading}
          autoCapitalize="none"
        />
        <TextInput
          placeholder="Password"
          value={password}
          onChangeText={setPassword}
          style={styles.input}
          secureTextEntry
          editable={!loading}
        />

        <TouchableOpacity
          style={[styles.button, loading && styles.buttonDisabled]}
          onPress={handleLogin}
          disabled={loading}
        >
          {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Login</Text>}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", alignItems: "center", padding: 20, backgroundColor: "#f5f5f5" },
  loginCard: { width: "100%", maxWidth: 400, backgroundColor: "#fff", borderRadius: 10, padding: 30, shadowColor: "#000", shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 8, elevation: 5 },
  title: { fontSize: 28, fontWeight: "bold", textAlign: "center", marginBottom: 30, color: "#333" },
  input: { borderWidth: 1, borderColor: "#ddd", borderRadius: 8, padding: 15, marginBottom: 15, fontSize: 16, backgroundColor: "#f9f9f9" },
  button: { backgroundColor: "#007bff", padding: 15, borderRadius: 8, alignItems: "center", marginTop: 10 },
  buttonDisabled: { backgroundColor: "#ccc" },
  buttonText: { color: "#fff", fontSize: 18, fontWeight: "600" },
});