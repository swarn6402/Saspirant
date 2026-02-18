import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import API_BASE_URL from '../config';

export default function Dashboard() {
    const { user } = useAuth();
    const [stats, setStats] = useState(null);
    const [alerts, setAlerts] = useState([]);
    const [urls, setUrls] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (user) {
            fetchDashboardData();
        }
    }, [user]);

    const formatDate = (dateStr) => {
        if (!dateStr) return 'N/A';
        const d = new Date(dateStr);
        return isNaN(d.getTime()) ? 'N/A' : d.toLocaleDateString();
    };

    const fetchDashboardData = async () => {
        try {
            // Fetch summary
            const summaryRes = await fetch(`${API_BASE_URL}/api/dashboard/${user.id}/summary`);
            const summaryData = await summaryRes.json();
            setStats(summaryData.stats);

            // Fetch alerts
            const alertsRes = await fetch(`${API_BASE_URL}/api/dashboard/${user.id}/alerts?page=1&per_page=10`);
            const alertsData = await alertsRes.json();
            setAlerts(Array.isArray(alertsData.alerts) ? alertsData.alerts : []);

            // Fetch monitored URLs
            const urlsRes = await fetch(`${API_BASE_URL}/api/preferences/${user.id}/urls`);
            const urlsData = await urlsRes.json();
            if (Array.isArray(urlsData)) setUrls(urlsData);
            else if (urlsData && Array.isArray(urlsData.urls)) setUrls(urlsData.urls);
            else setUrls([]);

            setLoading(false);
        } catch (err) {
            console.error('Error fetching dashboard data:', err);
            setLoading(false);
        }
    };

    const handleManualScrape = async (urlId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/dashboard/${user.id}/trigger-scrape/${urlId}`, {
                method: 'POST'
            });

            if (response.ok) {
                alert('Scrape triggered! Check your email for alerts.');
                fetchDashboardData(); // Refresh data
            }
        } catch (err) {
            console.error('Error triggering scrape:', err);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex flex-col">
                <Navbar />
                <div className="flex-grow flex items-center justify-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen flex flex-col">
            <Navbar />
            <main className="flex-grow bg-gray-50 py-8 px-4">
                <div className="max-w-7xl mx-auto">

                    {/* Header */}
                    <div className="mb-8">
                        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                        <p className="text-gray-500">Welcome back, {user.name.split(' ')[0]}! 👋</p>
                    </div>

                    {/* Stats Cards */}
                    <div className="grid md:grid-cols-4 gap-6 mb-8">
                        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                            <div className="text-gray-500 text-sm mb-1">Total Alerts</div>
                            <div className="text-3xl font-bold text-gray-900">{stats?.total_alerts_received || 0}</div>
                            <div className="text-green-600 text-sm mt-1">+{stats?.alerts_this_week || 0} this week</div>
                        </div>
                        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                            <div className="text-gray-500 text-sm mb-1">Monitored Sites</div>
                            <div className="text-3xl font-bold text-gray-900">{urls.length}</div>
                            <div className="text-gray-400 text-sm mt-1">Active monitoring</div>
                        </div>
                        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                            <div className="text-gray-500 text-sm mb-1">Next Deadline</div>
                            <div className="text-xl font-bold text-gray-900">
                                {alerts[0] ? formatDate(alerts[0].notification_date) : 'No alerts'}
                            </div>
                            <div className="text-gray-400 text-sm mt-1 truncate">
                                {alerts[0]?.job_title?.substring(0, 30) || 'No upcoming deadlines'}
                            </div>
                        </div>
                        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                            <div className="text-gray-500 text-sm mb-1">Match Rate</div>
                            <div className="text-3xl font-bold text-gray-900">{stats?.match_rate || 0}%</div>
                            <div className="text-gray-400 text-sm mt-1">Alerts matched preferences</div>
                        </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-6">

                        {/* Recent Alerts */}
                        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                            <div className="flex justify-between items-center mb-6">
                                <h2 className="text-lg font-bold text-gray-900">Recent Alerts</h2>
                                <span className="text-sm text-gray-500">{alerts.length} total</span>
                            </div>

                            {alerts.length === 0 ? (
                                <div className="text-center py-12">
                                    <div className="text-4xl mb-4">📭</div>
                                    <p className="text-gray-500">No alerts yet</p>
                                    <p className="text-sm text-gray-400 mt-2">We'll notify you when matching opportunities are posted</p>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    {alerts.slice(0, 5).map(alert => (
                                        <div key={alert.id} className="border border-gray-100 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                                            <h3 className="font-semibold text-gray-900 mb-1">{alert.job_title}</h3>
                                            <p className="text-sm text-gray-500">{alert.organization}</p>
                                            <div className="flex items-center justify-between mt-3">
                                                <span className="text-xs bg-indigo-50 text-indigo-700 px-2 py-1 rounded">
                                                    {alert.exam_category}
                                                </span>
                                                <a
                                                    href={alert.source_url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="text-sm text-indigo-600 hover:underline"
                                                >
                                                    View Details →
                                                </a>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Monitored Websites */}
                        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                            <div className="flex justify-between items-center mb-6">
                                <h2 className="text-lg font-bold text-gray-900">Monitored Websites</h2>
                                <Link to="/preferences" className="text-sm text-indigo-600 hover:underline">
                                    Manage
                                </Link>
                            </div>

                            {urls.length === 0 ? (
                                <div className="text-center py-12">
                                    <div className="text-4xl mb-4">🌐</div>
                                    <p className="text-gray-500">No websites added yet</p>
                                    <Link
                                        to="/preferences"
                                        className="inline-block mt-4 text-indigo-600 hover:underline text-sm"
                                    >
                                        Add websites to monitor →
                                    </Link>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    {urls.map(url => (
                                        <div key={url.id} className="border border-gray-100 rounded-lg p-4">
                                            <div className="flex justify-between items-start mb-2">
                                                <div className="flex-grow">
                                                    <h3 className="font-semibold text-gray-900">{url.website_name}</h3>
                                                    <p className="text-xs text-gray-400 break-all">{url.url}</p>
                                                </div>
                                            </div>
                                            <div className="flex items-center justify-between mt-3">
                                                <span className="text-xs text-gray-400">
                                                    {url.last_scraped_at ? `Last checked: ${formatDate(url.last_scraped_at)}` : 'Never checked'}
                                                </span>
                                                <button
                                                    onClick={() => handleManualScrape(url.id)}
                                                    className="text-xs bg-indigo-50 text-indigo-600 px-3 py-1 rounded hover:bg-indigo-100 transition-colors"
                                                >
                                                    Test Scrape
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Empty State CTA */}
                    {urls.length === 0 && alerts.length === 0 && (
                        <div className="mt-8 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-8 text-center">
                            <h3 className="text-xl font-bold text-gray-900 mb-2">Let's Get Started! 🚀</h3>
                            <p className="text-gray-600 mb-6">Add your exam preferences and websites to start receiving alerts</p>
                            <Link
                                to="/preferences"
                                className="inline-block bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors"
                            >
                                Set Up Preferences
                            </Link>
                        </div>
                    )}

                </div>
            </main>
            <Footer />
        </div>
    );
}
