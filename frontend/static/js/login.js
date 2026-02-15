async function handleLogin(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // Basic validation
    if (!email || !password) {
        showError('Please enter both email and password');
        return;
    }

    const formData = {
        email: email,
        password: password
    };

    console.log('Attempting login with:', email);

    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        console.log('Login response status:', response.status);

        if (response.ok) {
            const data = await response.json();
            console.log('Login successful:', data);

            // Store user info in localStorage
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('user_name', data.name);
            localStorage.setItem('user_email', data.email);

            // Show success message
            showSuccess('Login successful! Redirecting...');

            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = `/templates/dashboard.html?user_id=${data.user_id}`;
            }, 1000);
        } else {
            const errorData = await response.json();
            console.error('Login failed:', errorData);
            showError(errorData.error || 'Invalid email or password');
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('Login failed. Please try again.');
    }
}

// Helper functions (copy from register.js)
function showError(message) {
    // Display error message to user
    alert(message); // Simple version, can be styled better
}

function showSuccess(message) {
    alert(message);
}

// Attach event listener when page loads
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', handleLogin);
    }
});
