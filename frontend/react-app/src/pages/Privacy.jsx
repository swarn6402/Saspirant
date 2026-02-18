import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

export default function Privacy() {
  return (
    <div className="bg-gray-50 min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow">
        <div className="max-w-4xl mx-auto px-6 py-12">
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8">
            <h1 className="text-3xl font-extrabold text-gray-900">Privacy Policy</h1>
            <p className="text-sm text-gray-500 mt-2">Last updated: February 14, 2026</p>

            <section className="mt-8">
              <h2 className="text-xl font-bold text-gray-900 mb-3">1. Information We Collect</h2>
              <p className="text-sm text-gray-700 leading-relaxed">
                We collect your name, email, date of birth, highest qualification, exam preferences,
                and monitored website URLs.
              </p>
            </section>

            <section className="mt-8">
              <h2 className="text-xl font-bold text-gray-900 mb-3">2. How We Use Your Information</h2>
              <p className="text-sm text-gray-700 leading-relaxed">
                We use your information to match notifications to your preferences, send alerts, and
                show dashboard history. We do not sell personal information to third parties.
              </p>
            </section>

            <section className="mt-8">
              <h2 className="text-xl font-bold text-gray-900 mb-3">3. Data Storage</h2>
              <p className="text-sm text-gray-700 leading-relaxed">
                Data is stored in PostgreSQL hosted on Neon with reasonable technical and operational
                controls in place.
              </p>
            </section>

            <section className="mt-8">
              <h2 className="text-xl font-bold text-gray-900 mb-3">4. Email Delivery</h2>
              <p className="text-sm text-gray-700 leading-relaxed">
                We use SendGrid only for delivering notifications and service-related messages.
              </p>
            </section>

            <section className="mt-8">
              <h2 className="text-xl font-bold text-gray-900 mb-3">5. Your Rights</h2>
              <p className="text-sm text-gray-700 leading-relaxed">
                You can update your preferences from the dashboard anytime, request account deletion by
                contacting us, and contact us to correct inaccurate information.
              </p>
            </section>

            <section className="mt-8">
              <h2 className="text-xl font-bold text-gray-900 mb-3">6. Changes to This Policy</h2>
              <p className="text-sm text-gray-700 leading-relaxed">
                Major changes to this policy will update the &quot;Last updated&quot; date.
              </p>
            </section>

            <section className="mt-8">
              <h2 className="text-xl font-bold text-gray-900 mb-3">7. Contact</h2>
              <p className="text-sm text-gray-700 leading-relaxed">
                For privacy-related questions, contact us at{' '}
                <a href="mailto:swarnjeettiwary02@gmail.com" className="text-indigo-600 hover:underline">
                  swarnjeettiwary02@gmail.com
                </a>
                .
              </p>
            </section>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
