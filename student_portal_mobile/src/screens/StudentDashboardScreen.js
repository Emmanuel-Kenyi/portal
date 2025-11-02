import React from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    TouchableOpacity,
} from 'react-native';

const StudentDashboardScreen = ({ route, navigation }) => {
    const { data } = route.params;
    const profile = data.profile;
    const clubs = data.clubs || [];

    const handleLogout = () => {
        navigation.replace('Login');
    };

    return (
        <ScrollView style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.welcome}>Welcome, {profile.name}!</Text>
                <Text style={styles.role}>Role: {profile.role}</Text>
            </View>

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>My Clubs</Text>
                {clubs.length > 0 ? (
                    clubs.map((club) => (
                        <View key={club.id} style={styles.card}>
                            <Text style={styles.clubName}>{club.name}</Text>
                            <Text style={styles.clubDesc}>{club.description}</Text>
                        </View>
                    ))
                ) : (
                    <Text style={styles.noData}>No clubs joined yet</Text>
                )}
            </View>

            <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
                <Text style={styles.logoutText}>Logout</Text>
            </TouchableOpacity>
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    header: {
        backgroundColor: '#007AFF',
        padding: 20,
        paddingTop: 60,
    },
    welcome: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#fff',
        marginBottom: 5,
    },
    role: {
        fontSize: 16,
        color: '#fff',
        opacity: 0.9,
    },
    section: {
        padding: 20,
    },
    sectionTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        marginBottom: 15,
        color: '#333',
    },
    card: {
        backgroundColor: '#fff',
        padding: 15,
        borderRadius: 8,
        marginBottom: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    clubName: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 5,
    },
    clubDesc: {
        fontSize: 14,
        color: '#666',
    },
    noData: {
        fontSize: 16,
        color: '#999',
        textAlign: 'center',
        marginTop: 20,
    },
    logoutButton: {
        backgroundColor: '#FF3B30',
        padding: 15,
        borderRadius: 8,
        margin: 20,
        alignItems: 'center',
    },
    logoutText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: 'bold',
    },
});

export default StudentDashboardScreen;