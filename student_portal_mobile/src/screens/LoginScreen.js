import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import { loginUser, fetchDashboard } from '../client';

const LoginScreen = ({ navigation }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!username || !password) {
      Alert.alert('Error', 'Please enter username and password');
      return;
    }

    setLoading(true);
    try {
      const tokenData = await loginUser(username, password);
      const token = tokenData.access;

      const dashboardData = await fetchDashboard(token);
      const role = dashboardData.profile.role.toLowerCase();

      // attach token for future API calls
      const dashboardDataWithToken = { ...dashboardData, token };

      if (role === 'admin') navigation.replace('AdminDashboard', { data: dashboardDataWithToken });
      else if (role === 'lecturer') navigation.replace('LecturerDashboard', { data: dashboardDataWithToken });
      else if (role === 'student') navigation.replace('StudentDashboard', { data: dashboardDataWithToken });
      else Alert.alert('Error', 'Unknown user role');
    } catch (error) {
      console.log(error.response || error.message);
      Alert.alert('Login Failed', error.response?.data?.detail || error.response?.data || 'Invalid credentials');
      setUsername('');
      setPassword('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Student Portal</Text>
      <Text style={styles.subtitle}>Login to continue</Text>

      <TextInput style={styles.input} placeholder="Username" value={username} onChangeText={setUsername} autoCapitalize="none" />
      <TextInput style={styles.input} placeholder="Password" value={password} onChangeText={setPassword} secureTextEntry />

      <TouchableOpacity style={styles.button} onPress={handleLogin} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Login</Text>}
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 20, backgroundColor: '#f5f5f5' },
  title: { fontSize: 32, fontWeight: 'bold', textAlign: 'center', marginBottom: 10, color: '#333' },
  subtitle: { fontSize: 16, textAlign: 'center', marginBottom: 40, color: '#666' },
  input: { backgroundColor: '#fff', padding: 15, borderRadius: 8, marginBottom: 15, fontSize: 16, borderWidth: 1, borderColor: '#ddd' },
  button: { backgroundColor: '#007AFF', padding: 15, borderRadius: 8, alignItems: 'center', marginTop: 10 },
  buttonText: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
});

export default LoginScreen;
