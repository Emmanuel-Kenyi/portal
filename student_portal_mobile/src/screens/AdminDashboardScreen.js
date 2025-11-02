import React from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    TouchableOpacity,
} from 'react-native';

const AdminDashboardScreen = ({ route, navigation }) => {
    const { data } = route.params;
    const profile = data.profile;
    const summary = data.summary || {};

    const handleLogout = () => {
        navigation.replace('Login');
    };

    return (
        <ScrollView style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.welcome}>Admin Dashboard</Text>
                <Text style={styles.role}>Welcome, {profile.name}</Text>
            </View>

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>System Statistics</Text>
                
                <View style={styles.statsContainer}>
                    <View style={styles.statCard}>
                        <Text style={styles.statNumber}>{summary.total_users || 0}</Text>
                        <Text style={styles.statLabel}>Total Users</Text>
                    </View>

                    <View style={styles.statCard}>
                        <Text style={styles.statNumber}>{summary.total_students || 0}</Text>
                        <Text style={styles.statLabel}>Students</Text>
                    </View>

                    <View style={styles.statCard}>
                        <Text style={styles.statNumber}>{summary.total_lecturers || 0}</Text>
                        <Text style={styles.statLabel}>Lecturers</Text>
                    </View>

                    <View style={styles.statCard}>
                        <Text style={styles.statNumber}>{summary.total_clubs || 0}</Text>
                        <Text style={styles.statLabel}>Clubs</Text>
                    </View>
                </View>
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
        backgroundColor: '#34C759',
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
    statsContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
    },
    statCard: {
        backgroundColor: '#fff',
        padding: 20,
        borderRadius: 8,
        width: '48%',
        marginBottom: 15,
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    statNumber: {
        fontSize: 32,
        fontWeight: 'bold',
        color: '#34C759',
        marginBottom: 5,
    },
    statLabel: {
        fontSize: 14,
        color: '#666',
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

export default AdminDashboardScreen;