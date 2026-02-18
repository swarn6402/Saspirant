import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import API_BASE_URL from '../config';

export default function Preferences() {
    const { user } = useAuth();
    const navigate = useNavigate();
    
    const [categories, setCategories] = useState([]);
    const [urls, setUrls] = useState([]);
    const [newUrl, setNewUrl] = useState('');
    const [newWebsiteName, setNewWebsiteName] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');

    const examCategories = ['UPSC', 'SSC', 'Banking', 'Railways', 'State PSC', 'University', 'Defence', 'Teaching', 'Medical', 'Engineering'];

    useEffect(() => {
        if (user) {
            fetchPreferences();
            fetchUrls();
        }
    }, [user]);

    const fetchPreferences = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/preferences/${user.id}`);
            const data = await response.json();
            if (Array.isArray(data)) {
                setCategories(data.map(p => p.exam_category));
            }
        } catch (err) {
            console.error('Error fetching preferences:', err);
        }
    };

    const fetchUrls = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/preferences/${user.id}/urls`);
            const data = await response.json();
            setUrls(data || []);
        } catch (err) {
            console.error('Error fetching URLs:', err);
        }
    };

    const handleCategoryToggle = (category) => {
        setCategories(prev =>
            prev.includes(category)
                ? prev.filter(c => c !== category)
                : [...prev, category]
        );
    };

    const handleAddUrl = async (e) => {
        e.preventDefault();
        if (!newUrl || !newWebsiteName) return;

        try {
            const response = await fetch(`${API_BASE_URL}/api/preferences/${user.id}/urls`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: newUrl,
                    website_name: newWebsiteName,
                    scraper_type: 'html'
                })
            });

            if (response.ok) {
                setNewUrl('');
                setNewWebsiteName('');
                fetchUrls();
                setMessage('Website added successfully!');
            } else {
                const errorData = await response.json();
                setMessage('Failed to add URL: ' + (errorData.error || 'Invalid URL'));
            }
        } catch (err) {
            console.error('Error adding URL:', err);
            setMessage('Failed to add URL: ' + err.message);
        }
    };

    const handleRemoveUrl = async (urlId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/preferences/${user.id}/urls/${urlId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                fetchUrls();
            }
        } catch (err) {
            console.error('Error removing URL:', err);
        }
    };

    const handleSave = async () => {
        if (categories.length === 0) {
            setMessage('Please select at least one exam category');
            return;
        }

        setLoading(true);
        setMessage('');

        try {
            const response = await fetch(`${API_BASE_URL}/api/preferences/${user.id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    exam_categories: categories,
                    min_age: 18,
                    max_age: 35,
                    preferred_locations: ['All India']
                })
            });

            if (response.ok) {
                setMessage('Preferences saved successfully!');
                setTimeout(() => navigate('/dashboard'), 1500);
            } else {
                setMessage('Failed to save preferences');
            }
        } catch (err) {
            setMessage('Error saving preferences');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex flex-col">
            <Navbar />
            <main className="flex-grow bg-gray-50 py-12 px-4">
                <div className="max-w-4xl mx-auto">
                    
                    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 mb-6">
                        <h1 className="text-2xl font-bold text-gray-900 mb-2">Set Your Preferences</h1>
                        <p className="text-gray-500 mb-8">Choose exam categories you're interested in</p>

                        {message && (
                            <div className={`mb-6 px-4 py-3 rounded-lg ${message.includes('success') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                                {message}
                            </div>
                        )}

                        {/* Exam Categories */}
                        <div className="mb-8">
                            <h2 className="font-semibold text-gray-900 mb-4">Select Exam Categories</h2>
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                {examCategories.map(category => (
                                    <button
                                        key={category}
                                        onClick={() => handleCategoryToggle(category)}
                                        className={`px-4 py-3 rounded-lg border-2 transition-all ${
                                            categories.includes(category)
                                                ? 'border-indigo-600 bg-indigo-50 text-indigo-700 font-semibold'
                                                : 'border-gray-200 hover:border-gray-300'
                                        }`}
                                    >
                                        {category}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Add URLs */}
                        <div className="mb-8">
                            <h2 className="font-semibold text-gray-900 mb-4">Add Websites to Monitor</h2>
                            <form onSubmit={handleAddUrl} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Website Name</label>
                                    <input
                                        type="text"
                                        value={newWebsiteName}
                                        onChange={(e) => setNewWebsiteName(e.target.value)}
                                        placeholder="e.g., UPSC Official"
                                        className="w-full border border-gray-200 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Website URL</label>
                                    <input
                                        type="url"
                                        value={newUrl}
                                        onChange={(e) => setNewUrl(e.target.value)}
                                        placeholder="https://upsc.gov.in/examinations"
                                        className="w-full border border-gray-200 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                    />
                                </div>
                                <button
                                    type="submit"
                                    className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
                                >
                                    Add Website
                                </button>
                            </form>
                        </div>

                        {/* Monitored URLs List */}
                        {urls.length > 0 && (
                            <div className="mb-8">
                                <h2 className="font-semibold text-gray-900 mb-4">Monitored Websites ({urls.length})</h2>
                                <div className="space-y-3">
                                    {urls.map(url => (
                                        <div key={url.id} className="flex items-center justify-between bg-gray-50 rounded-lg p-4">
                                            <div>
                                                <h3 className="font-medium text-gray-900">{url.website_name}</h3>
                                                <p className="text-sm text-gray-500 break-all">{url.url}</p>
                                            </div>
                                            <button
                                                onClick={() => handleRemoveUrl(url.id)}
                                                className="text-red-500 hover:text-red-700 ml-4"
                                            >
                                                Remove
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Save Button */}
                        <button
                            onClick={handleSave}
                            disabled={loading || categories.length === 0}
                            className="w-full bg-indigo-600 text-white font-semibold py-3 rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
                        >
                            {loading ? 'Saving...' : 'Save Preferences & Continue'}
                        </button>
                    </div>

                </div>
            </main>
            <Footer />
        </div>
    );
}
