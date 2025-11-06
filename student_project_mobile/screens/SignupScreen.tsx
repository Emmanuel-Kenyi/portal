import React, { useState } from "react";
import { View, TextInput, TouchableOpacity, Text, StyleSheet, Alert, ActivityIndicator, KeyboardAvoidingView, Platform } from "react-native";
import { apiPost } from "../utils/api";

interface SignupResponse {
  id: number;
  username: string;
  email: string;
}

export default function SignupScreen() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password1, setPassword1] = useState("");
  const [password2, setPassword2] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSignup = async () => {
    if (!username || !email || !password1 || !password2) {
      Alert.alert("Error", "Please fill all fields");
      return;
    }

    if (password1 !== password2) {
      Alert.alert("Error", "Passwords do not match");
      return;
    }

    setLoading(true);

    const data = await apiPost<{ username: string; email: string; password1: string; password2: string }, SignupResponse>(
      "signup/",
      { username, email, password1, password2 }
    );

    setLoading(false);

    if (data) {
      Alert.alert("Success", `Account created for ${data.username}`);
      setUsername(""); setEmail(""); setPassword1(""); setPassword2("");
    }
  };

  return (
    <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} style={styles.container}>
      <View style={styles.signupCard}>
        <Text style={styles.title}>Sign Up</Text>
        <TextInput placeholder="Username" value={username} onChangeText={setUsername} style={styles.input} editable={!loading} />
        <TextInput placeholder="Email" value={email} onChangeText={setEmail} style={styles.input} editable={!loading} keyboardType="email-address" />
        <TextInput placeholder="Password" value={password1} onChangeText={setPassword1} style={styles.input} secureTextEntry editable={!loading} />
        <TextInput placeholder="Confirm Password" value={password2} onChangeText={setPassword2} style={styles.input} secureTextEntry editable={!loading} />
        <TouchableOpacity style={[styles.button, loading && styles.buttonDisabled]} onPress={handleSignup} disabled={loading}>
          {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Sign Up</Text>}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", alignItems: "center", padding: 20, backgroundColor: "#f5f5f5" },
  signupCard: { width: "100%", maxWidth: 400, backgroundColor: "#fff", borderRadius: 10, padding: 30, shadowColor: "#000", shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 8, elevation: 5 },
  title: { fontSize: 28, fontWeight: "bold", textAlign: "center", marginBottom: 30, color: "#333" },
  input: { borderWidth: 1, borderColor: "#ddd", borderRadius: 8, padding: 15, marginBottom: 15, fontSize: 16, backgroundColor: "#f9f9f9" },
  button: { backgroundColor: "#28a745", padding: 15, borderRadius: 8, alignItems: "center", marginTop: 10 },
  buttonDisabled: { backgroundColor: "#ccc" },
  buttonText: { color: "#fff", fontSize: 18, fontWeight: "600" },
});
